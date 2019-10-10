import pytest

from domehunter.dome_control import *


@pytest.fixture
def testing_dome(scope='function'):
    dome = Dome(testing=True, debug_lights=False)
    return dome


@pytest.fixture
def dome_az_90(scope='function'):
    dome = Dome(testing=True, debug_lights=False)
    dome._dome_az = Longitude(90 * u.deg)
    dome._degrees_per_tick = Angle(10 * u.deg)
    dome._home_sensor_pin.drive_low()
    dome._encoder_count = 9
    return dome


def test_dome_initialisation(testing_dome):
    assert testing_dome.testing is True
    assert testing_dome.dome_in_motion is False
    assert testing_dome.dome_az.degree == 0
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


def test_abort(testing_dome):
    # This test should test that GotoAz() is non-blocking
    # but haven't implemented that yet
    testing_dome._rotation_relay.on()
    assert testing_dome.dome_in_motion is True
    testing_dome.abort()
    assert testing_dome.dome_in_motion is False


def test_dome_az(dome_az_90):
    assert dome_az_90.dome_az == 90
    assert dome_az_90.dome_az == dome_az_90.dome_az.degree


def test_GotoAz(dome_az_90):
    # test fixture has degrees_per_tick attribute of 10
    dome_az_90.GotoAz(300)
    assert dome_az_90.dome_az == Angle(300 * u.deg)
    assert dome_az_90.encoder_count == -6
    dome_az_90.GotoAz(2)
    assert dome_az_90.dome_az == Angle(10 * u.deg)
    assert dome_az_90.encoder_count == 1


@pytest.mark.calibrate
def test_calibrate_dome_encoder_counts(testing_dome):
    testing_dome.calibrate_dome_encoder_counts()
    assert testing_dome.dome_az == 0
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
    if dname == "CW" or dname is "NONE" and ldname == "CW":
        expected = 10
    elif dname == "CCW" or dname is "NONE" and ldname == "CCW":
        expected = 8
    dome_az_90.current_direction = current_dir
    dome_az_90.last_direction = last_dir
    dome_az_90._increment_count()
    assert dome_az_90.encoder_count == expected
