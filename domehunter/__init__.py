"""Run dome control a raspberry pi GPIO."""

# Licensed under a 3-clause BSD style license - see LICENSE.rst

# Packages may add whatever they like to this file, but
# should keep this content at the top.
# ----------------------------------------------------------------------------
from gpiozero import DigitalInputDevice, Device
from gpiozero.pins.mock import MockFactory

from ._astropy_init import *
# ----------------------------------------------------------------------------

# Enforce Python version check during package import.
# This is the same check as the one at the top of setup.py
import sys

__minimum_python_version__ = "3.7"


class UnsupportedPythonError(Exception):
    pass


if sys.version_info < tuple((int(val) for val in __minimum_python_version__.split('.'))):
    raise UnsupportedPythonError(
        "domehunter does not support Python < {}".format(__minimum_python_version__))

if not _ASTROPY_SETUP_:
    # For egg_info test builds to pass, put package imports here.
    pass


class X2DomeRPC():
    """Dummy class until real RPC class is available."""

    def __init__(self, *args, **kwargs):
        """Create dummy class until real RPC class is available."""


class Dome(X2DomeRPC):
    """
    Interface to dome control raspberry pi GPIO.

    Might start with: https://gpiozero.readthedocs.io/en/stable/
    but might use something else if we buy a fancy Pi HAT.
    """

    def __init__(self, testing=True, *args, **kwargs):
        """Initialize raspberry pi GPIO environment."""
        if testing:
            # Set the default pin factory to a mock factory
            Device.pin_factory = MockFactory()

            ENCODER_PIN_NUMBER = 7
            HOME_SENSOR_PIN_NUMBER = 11
        else:
            """ Do not change until you're sure!!! """
            # https://pinout.xyz/pinout/automation_hat
            ENCODER_PIN_NUMBER = None
            HOME_SENSOR_PIN_NUMBER = None

        self.dome_status = "unknown"

        self.encoder_count = 0
        self.encoder = DigitalInputDevice(ENCODER_PIN_NUMBER)
        self.encoder.when_activated = self._increment_count

        self._at_home = False
        self.home_sensor = DigitalInputDevice(HOME_SENSOR_PIN_NUMBER)
        self.home_sensor.when_deactivated = self._set_not_home()
        self.home_sensor.when_activated = self._set_at_home()

        self.dome_status = "unknown"

##################################################################################################
# Properties
##################################################################################################

    @property
    def is_home(self):
        """Send True if the dome is at home."""
        return self._at_home

    @property
    def status(self):
        """Return a text string describing dome rotators current status."""
        pass


##################################################################################################
# Methods
##################################################################################################

    """These map directly onto the AbstractMethods created by RPC."""

    def abort(self):
        """Stop everything."""
        pass

    def getAzEl(self):
        """Return AZ and Elevation."""
        pass

    def start_daemon(self):
        """Maybe start the RCP daemon here?."""
        raise NotImplementedError

    def halt_daemon(self):
        """Maybe start the RCP daemon here?."""
        raise NotImplementedError

##################################################################################################
# Private Methods
##################################################################################################

    def _set_at_home(self):
        self._at_home = True

    def _set_not_home(self):
        self._at_home = False

    def _increment_count(self, device=None):
        print(f"{device} activated _increment_count")
        if self.current_direction == "CW":
            self.encoder_count += 1
        elif self.current_direction == "CCW":
            self.encoder_count -= 1
        elif self.current_direction is None:
            if self.last_direction == "CW":
                self.encoder_count += 1
            elif self.last_direction == "CCW":
                self.encoder_count -= 1

    def _move_west(self, degrees_west):
        print(f"Moving {degrees_west} West")
        if self._west_is_ccw:
            cmd_status = self.move_ccw(degrees_west)
        else:
            cmd_status = self.move_cw(degrees_west)

        return cmd_status

    def _move_cw(self, degrees):
        print(f"Sending GPIO move_cw({degrees}) command.")
        self.current_direction = "CW"
        cmd_status = True
        return cmd_status

    def _move_ccw(self, degrees):
        print(f"Sending GPIO move_ccw({degrees}) command.")
        self.current_direction = "CCW"
        cmd_status = True
        return cmd_status
