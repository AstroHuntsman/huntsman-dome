import pytest

import domehunter


@pytest.fixture
def testing_dome(scope='function'):
    dome = domehunter.Dome(testing=True, debug_lights=False)
    return dome


@pytest.fixture
def dome_az_90(scope='function'):
    dome = domehunter.Dome(testing=True, debug_lights=False)
    dome.dome_az = 90
    dome.az_per_tick = 10
    dome.home_sensor_pin.drive_low()
    dome.encoder_count = 9
    return dome


def test_dome_initialisation(testing_dome):
    assert testing_dome.testing is True
    assert testing_dome._dome_status == "unknown"
    assert testing_dome.dome_az is None
    assert testing_dome.encoder_count == 0
    assert testing_dome.az_per_tick == 1
    assert testing_dome._at_home is False
    assert testing_dome.current_direction == "CCW"


def test_is_home(testing_dome):
    assert testing_dome.is_home is False
    testing_dome._at_home = True
    assert testing_dome.is_home is True


def test_status(testing_dome):
    assert testing_dome.status == "unknown"


def test_abort(testing_dome):
    testing_dome._move_cw()
    assert testing_dome.rotation_relay.is_active is True
    testing_dome.abort()
    assert testing_dome.rotation_relay.is_active is False


def test_getAz(dome_az_90):
    assert dome_az_90.getAz() == 90
    assert dome_az_90.getAz() == dome_az_90.dome_az
    # if dome_az is None, the dome should automatically calibrate itself
    # check that the calibration ended succesfully at home position
    dome_az_90.dome_az = None
    assert dome_az_90.getAz() == 0
    assert dome_az_90.az_per_tick == 36


def test_GotoAz(dome_az_90):
    dome_az_90.GotoAz(300)
    assert dome_az_90.dome_az == 290
    assert dome_az_90.encoder_count == 29
    dome_az_90.GotoAz(2)
    assert dome_az_90.dome_az == 10
    assert dome_az_90.encoder_count == 1


@pytest.mark.parametrize("current_dir", ["CW", "CCW", None])
@pytest.mark.parametrize("last_dir", ["CW", "CCW", None])
def test_increment_count(dome_az_90, current_dir, last_dir):
    if current_dir == "CW" or current_dir is None and last_dir == "CW":
        expected = 10
    elif current_dir == "CCW" or current_dir is None and last_dir == "CCW":
        expected = 8
    else:
        expected = 9
    dome_az_90.current_direction = current_dir
    dome_az_90.last_direction = last_dir
    dome_az_90._increment_count()
    assert dome_az_90.encoder_count == expected
