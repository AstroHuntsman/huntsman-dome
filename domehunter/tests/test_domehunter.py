import pytest
import time
import astropy.units as u
from astropy.coordinates import Angle, Longitude
from domehunter.dome_control import Dome
from domehunter.enumerations import Direction


@pytest.fixture
def testing_dome(scope='function'):
    home_az = 0
    dome = Dome(home_az, degrees_per_tick=1, testing=True, debug_lights=False)
    return dome


@pytest.fixture
def dome_az_90(scope='function'):
    home_az = 0
    dome = Dome(home_az, testing=True, debug_lights=False)
    # trigger a home to set dome.homed=True
    dome._home_sensor_pin.drive_high()
    # now that dome is homed manually set a new az
    dome._dome_az = Longitude(90 * u.deg)
    dome._degrees_per_tick = Angle(10 * u.deg)
    dome._encoder_count = 9
    return dome


def test_dome_initialisation(testing_dome):
    assert testing_dome.testing is True
    assert testing_dome.dome_in_motion is False
    assert testing_dome.dome_az.value == 0
    assert testing_dome.encoder_count == 0
    assert testing_dome.degrees_per_tick == Angle(1 * u.deg)
    assert testing_dome.at_home is False
    assert testing_dome.current_direction.name == "CCW"
    assert bool(testing_dome.current_direction.value + 1) is False


def test_at_home(testing_dome):
    assert testing_dome.at_home is False
    testing_dome._home_sensor_pin.drive_high()
    assert testing_dome.at_home is True


def test_status(testing_dome):
    testing_dome._rotation_relay.on()
    assert testing_dome.dome_in_motion is True
    testing_dome._rotation_relay.off()
    assert testing_dome.dome_in_motion is False


def test_abort(dome_az_90):
    dome_az_90.goto_az(300)
    time.sleep(0.5)
    assert dome_az_90.movement_thread_active
    assert dome_az_90.dome_in_motion
    time.sleep(0.5)
    dome_az_90.abort()
    assert not dome_az_90.movement_thread_active
    assert not dome_az_90.dome_in_motion


def test_park(dome_az_90):
    assert not dome_az_90.is_parked

    dome_az_90.park()
    assert dome_az_90.is_parked
    dome_offset_from_park = dome_az_90.dome_az - dome_az_90.park_az
    assert dome_offset_from_park <= dome_az_90.az_position_tolerance

    dome_az_90.goto_az(120)
    dome_offset_from_park = dome_az_90.dome_az - dome_az_90.park_az
    assert dome_offset_from_park <= dome_az_90.az_position_tolerance

    dome_az_90.unpark()
    dome_az_90.goto_az(120)
    while dome_az_90.movement_thread_active:
        time.sleep(1)
    dome_offset_from_requested_az = dome_az_90.dome_az - Longitude(120 * u.deg)
    assert dome_offset_from_requested_az <= dome_az_90.az_position_tolerance


def test_dome_az(dome_az_90, testing_dome):
    assert dome_az_90.dome_az == Longitude(90 * u.deg)
    assert testing_dome.dome_az == Longitude(0 * u.deg)


def test_goto_az(dome_az_90):
    # test fixture has degrees_per_tick attribute of 10
    dome_az_90.goto_az(300)
    while dome_az_90.movement_thread_active:
        time.sleep(1)
    assert dome_az_90.dome_az == Angle(310 * u.deg)
    assert dome_az_90.encoder_count == -5
    dome_az_90.goto_az(2)
    while dome_az_90.movement_thread_active:
        time.sleep(1)
    assert dome_az_90.dome_az == Angle(350 * u.deg)
    assert dome_az_90.encoder_count == -1


@pytest.mark.calibrate
def test_calibrate_dome_encoder_counts(testing_dome):
    testing_dome.calibrate_dome_encoder_counts()
    while testing_dome.movement_thread_active:
        time.sleep(1)
    assert testing_dome.encoder_count == 20
    assert testing_dome.degrees_per_tick == Angle(36 * u.deg)


def test_sync(dome_az_90):
    dome_az_90.sync(30)
    assert dome_az_90.encoder_count == 3


@pytest.mark.parametrize("current_dir", [Direction.CW,
                                         Direction.CCW,
                                         Direction.NONE])
@pytest.mark.parametrize("last_dir", [Direction.CW,
                                      Direction.CCW])
def test_increment_count(dome_az_90, current_dir, last_dir):
    dname = current_dir.name
    ldname = last_dir.name
    if dname == "CW" or dname == "NONE" and ldname == "CW":
        expected = 10
    elif dname == "CCW" or dname == "NONE" and ldname == "CCW":
        expected = 8
    dome_az_90.current_direction = current_dir
    dome_az_90.last_direction = last_dir
    dome_az_90._increment_count()
    assert dome_az_90.encoder_count == expected
