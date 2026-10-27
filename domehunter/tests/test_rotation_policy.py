"""Rotation direction policy: CW-only planning, long-way hold, and the gRPC calls."""
import os
import sys
import time
from concurrent import futures

import astropy.units as u
import grpc
import pytest
from astropy.coordinates import Angle, Longitude

from domehunter.dome_control import Dome
from domehunter.enumerations import Direction

SERVER_DIR = os.path.join(os.path.dirname(__file__), '..', 'gRPC-server')


def make_dome(**kwargs):
    dome = Dome(0, testing=True, degrees_per_tick=10, az_position_tolerance=1.0,
                log_file_level='CRITICAL', log_stderr_level='CRITICAL', **kwargs)
    dome._unhomed = False
    directions = []
    rotate = dome._rotate_dome

    def spy(direction):
        directions.append(direction)
        rotate(direction)

    dome._rotate_dome = spy
    dome.directions = directions
    return dome


def set_az(dome, az):
    dome._encoder_count = dome._az_to_ticks(Longitude(az * u.deg))


def wait_idle(dome, timeout=60):
    start = time.monotonic()
    while dome.movement_thread_active or dome.long_way_pending:
        assert time.monotonic() - start < timeout, 'dome never went idle'
        time.sleep(0.05)


def az_error(dome, target):
    return abs(((dome.dome_az.degree - target + 180) % 360) - 180)


# ── planning ──

@pytest.mark.parametrize('allowed, start, target, expected, long_way', [
    ('both', 100, 60, Direction.CCW, False),
    ('both', 100, 140, Direction.CW, False),
    ('CW', 100, 140, Direction.CW, False),
    ('CW', 100, 96, Direction.CCW, False),     # within max_reverse
    ('CW', 100, 60, Direction.CW, True),       # long way round
    ('CW', 350, 10, Direction.CW, False),      # CW through north
    ('CW', 10, 350, Direction.CW, True),
    ('CW', 100, 100.5, Direction.NONE, False),
])
def test_plan_move(allowed, start, target, expected, long_way):
    dome = make_dome(allowed_direction=allowed, max_reverse_degrees=5)
    dome._degrees_per_tick = Angle(0.1 * u.deg)
    set_az(dome, start)
    direction, _, is_long_way = dome._plan_move(Longitude(target * u.deg))
    assert direction == expected
    assert is_long_way == long_way


def test_long_way_goto_travels_and_completes():
    """A CW move over 180 deg must actually travel, not complete immediately."""
    dome = make_dome(allowed_direction='CW', max_reverse_degrees=5)
    set_az(dome, 100)
    dome.goto_az(60)
    wait_idle(dome)
    assert dome.directions == [Direction.CW]
    assert az_error(dome, 60) <= 15


def test_both_unchanged_default():
    dome = make_dome()
    assert dome.rotation_policy['allowed_direction'] == 'both'
    set_az(dome, 100)
    dome.goto_az(60)
    wait_idle(dome)
    assert dome.directions == [Direction.CCW]


# ── long-way hold ──

def test_hold_then_move():
    dome = make_dome(allowed_direction='CW', max_reverse_degrees=5,
                     long_way_settle_seconds=1)
    set_az(dome, 100)
    dome.goto_az(60)
    assert dome.long_way_pending and not dome.dome_in_motion
    time.sleep(0.5)
    dome.goto_az(62)                            # small update keeps the hold
    time.sleep(0.9)
    assert dome.directions == [Direction.CW]
    wait_idle(dome)


def test_hold_cancelled_by_short_request():
    dome = make_dome(allowed_direction='CW', max_reverse_degrees=5,
                     long_way_settle_seconds=1)
    set_az(dome, 100)
    dome.goto_az(60)
    dome.goto_az(103)                           # e.g. a meridian flip settling
    wait_idle(dome)
    time.sleep(1.5)
    assert not dome.long_way_pending
    assert Direction.CCW not in dome.directions
    assert dome.directions.count(Direction.CW) <= 1


def test_abort_clears_hold():
    dome = make_dome(allowed_direction='CW', long_way_settle_seconds=1)
    set_az(dome, 100)
    dome.goto_az(60)
    dome.abort()
    time.sleep(1.5)
    assert not dome.long_way_pending
    assert dome.directions == []


def test_park_skips_hold():
    dome = make_dome(allowed_direction='CW', long_way_settle_seconds=60)
    set_az(dome, 100)
    assert dome.park() == 0
    assert dome.directions == [Direction.CW]


# ── set_rotation_policy ──

def test_set_policy_switches_mode():
    dome = make_dome()
    assert dome.set_rotation_policy('CW', 5, 30, 4) == 0
    assert dome.rotation_policy == {
        'allowed_direction': 'CW', 'max_reverse_degrees': 5.0,
        'long_way_settle_seconds': 30.0, 'long_way_settle_tolerance': 4.0}
    assert dome.set_rotation_policy('both') == 0
    assert dome.rotation_policy['allowed_direction'] == 'both'


@pytest.mark.parametrize('kwargs', [
    {'allowed_direction': 'CCW'},
    {'allowed_direction': 'CW', 'max_reverse_degrees': -1},
    {'allowed_direction': 'CW', 'max_reverse_degrees': 180},
    {'allowed_direction': 'CW', 'long_way_settle_seconds': -5},
])
def test_set_policy_rejects_invalid(kwargs):
    dome = make_dome()
    with pytest.raises(ValueError):
        dome.set_rotation_policy(**kwargs)
    assert dome.rotation_policy['allowed_direction'] == 'both'


def test_set_policy_refused_while_holding():
    dome = make_dome(allowed_direction='CW', long_way_settle_seconds=60)
    set_az(dome, 100)
    dome.goto_az(60)
    assert dome.set_rotation_policy('both') == 1
    assert dome.rotation_policy['allowed_direction'] == 'CW'
    dome.abort()


# ── gRPC ──

@pytest.fixture
def rpc():
    """A real gRPC server around a testing Dome, and a stub connected to it."""
    sys.path.insert(0, SERVER_DIR)
    try:
        import huntsman_dome_server as srv
        import hx2dome_pb2 as pb
        import hx2dome_pb2_grpc as pb_grpc
    finally:
        sys.path.remove(SERVER_DIR)

    class Logger:
        def __getattr__(self, name):
            return lambda *a, **k: None

    servicer = srv.HX2DomeServer(
        0, Logger(), testing=True, server_testing=False, degrees_per_tick=10,
        log_file_level='CRITICAL', log_stderr_level='CRITICAL')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    pb_grpc.add_HX2DomeServicer_to_server(servicer, server)
    port = server.add_insecure_port('127.0.0.1:0')
    server.start()
    channel = grpc.insecure_channel(f'127.0.0.1:{port}')
    yield pb, pb_grpc.HX2DomeStub(channel), servicer.dome
    channel.close()
    server.stop(0)


def test_rpc_default_policy_is_both(rpc):
    pb, stub, _ = rpc
    policy = stub.dapiGetRotationPolicy(pb.Empty(), timeout=5)
    assert policy.return_code == 0
    assert policy.allowed_direction == 'both'


def test_rpc_set_and_get(rpc):
    pb, stub, dome = rpc
    reply = stub.dapiSetRotationPolicy(
        pb.RotationPolicy(allowed_direction='CW', max_reverse_degrees=5,
                          long_way_settle_seconds=60, long_way_settle_tolerance=5),
        timeout=5)
    assert reply.return_code == 0
    assert dome.cw_only
    policy = stub.dapiGetRotationPolicy(pb.Empty(), timeout=5)
    assert (policy.allowed_direction, policy.max_reverse_degrees,
            policy.long_way_settle_seconds) == ('CW', 5.0, 60.0)


def test_rpc_invalid_policy(rpc):
    pb, stub, dome = rpc
    reply = stub.dapiSetRotationPolicy(
        pb.RotationPolicy(allowed_direction='sideways'), timeout=5)
    assert reply.return_code == 2
    assert 'allowed_direction' in reply.error_message
    assert not dome.cw_only


def test_rpc_existing_calls_unaffected(rpc):
    """The calls TheSkyX's driver makes still work alongside the new ones."""
    pb, stub, _ = rpc
    assert stub.dapiGetAzEl(pb.Empty(), timeout=5).return_code in (0, 1)
    assert stub.dapiIsGotoComplete(pb.Empty(), timeout=5).is_complete


def test_stubs_importable_from_package():
    """Installed domehunter exposes the generated stubs (for SensorKit's client)."""
    from domehunter.hx2dome import pb2, pb2_grpc

    policy = pb2.RotationPolicy(allowed_direction='CW', max_reverse_degrees=5)
    assert pb2.RotationPolicy.FromString(policy.SerializeToString()) == policy
    assert hasattr(pb2_grpc, 'HX2DomeStub')


def test_config_file_defaults_to_cw():
    """The shipped config makes clockwise-only the default (CCW damages the dome)."""
    from domehunter.dome_control import load_dome_config

    config = load_dome_config(os.path.join(SERVER_DIR, 'dome_controller_config.yml'))
    assert config['allowed_direction'] == 'CW'
    dome = make_dome(**{k: config[k] for k in (
        'allowed_direction', 'max_reverse_degrees',
        'long_way_settle_seconds', 'long_way_settle_tolerance')})
    policy = dome.rotation_policy
    assert policy['allowed_direction'] == 'CW'
    assert all(type(v) is float for k, v in policy.items() if k != 'allowed_direction')
