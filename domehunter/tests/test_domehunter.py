import pytest

from domehunter.dome_control import *


@pytest.fixture
def testing_dome(scope='function'):
    dome = Dome(testing=True, debug_lights=False)
    return dome


@pytest.fixture
def dome_az_90(scope='function'):
    dome = Dome(testing=True, debug_lights=False)
    dome._Dome__dome_az = 90
    dome._Dome__az_per_tick = 10
    dome._Dome__home_sensor_pin.drive_low()
    dome._Dome__encoder_count = 9
    return dome


def test_dome_initialisation(testing_dome):
    assert testing_dome.testing is True
    assert testing_dome.dome_in_motion is False
    assert testing_dome.dome_az.degree == 0
    assert testing_dome.encoder_count == 0
    assert testing_dome.az_per_tick == 1
    assert testing_dome.at_home is False
    assert testing_dome.current_direction.name == "CCW"
    assert testing_dome.current_direction.value is False


def test_at_home(testing_dome):
    assert testing_dome.at_home is False
    testing_dome._Dome__home_sensor_pin.drive_high()
    assert testing_dome.at_home is True


def test_status(testing_dome):
    testing_dome._Dome__rotation_relay.on()
    assert testing_dome.dome_in_motion is True
    testing_dome._Dome__rotation_relay.off()
    assert testing_dome.dome_in_motion is False


def test_abort(testing_dome):
    # This test should test that GotoAz() is non-blocking
    # but haven't implemented that yet
    testing_dome._Dome__rotation_relay.on()
    assert testing_dome.dome_in_motion is True
    testing_dome.abort()
    assert testing_dome.dome_in_motion is False


def test_getAz(dome_az_90):
    assert dome_az_90.getAz() == 90
    assert dome_az_90.getAz() == dome_az_90.dome_az.degree


def test_GotoAz(dome_az_90):
    # test fixture has az_per_tick attribute of 10
    dome_az_90.GotoAz(300)
    assert dome_az_90._Dome__encoder_count == -5
    dome_az_90.GotoAz(2)
    assert dome_az_90.dome_az.degree == 0
    assert dome_az_90.encoder_count == 0


@pytest.mark.calibrate
def test_calibrate_dome_encoder_counts(testing_dome):
    testing_dome.calibrate_dome_encoder_counts()
    assert testing_dome.dome_az == 0
    assert testing_dome.encoder_count == 20
    assert testing_dome.az_per_tick == 36

def test_sync(dome_az_90):
    dome_az_90.sync(30)
    assert dome_az_90.encoder_count == 3


@pytest.mark.parametrize("current_dir", [Direction.CW,
                                         Direction.CCW,
                                         Direction.none])
@pytest.mark.parametrize("last_dir", [Direction.CW,
                                      Direction.CCW])
def test_increment_count(dome_az_90, current_dir, last_dir):
    dname = current_dir.name
    ldname = last_dir.name
    if dname == "CW" or dname is "none" and ldname == "CW":
        expected = 10
    elif dname == "CCW" or dname is "none" and ldname == "CCW":
        expected = 8
    dome_az_90.current_direction = current_dir
    dome_az_90.last_direction = last_dir
    dome_az_90._increment_count()
    assert dome_az_90.encoder_count == expected
