"""Run dome control on a raspberry pi GPIO."""

# Licensed under a 3-clause BSD style license - see LICENSE.rst
# should keep this content at the top.
# ----------------------------------------------------------------------------
import sys
import time

from gpiozero import Device, DigitalInputDevice, DigitalOutputDevice
from gpiozero.pins.mock import MockFactory

from ._astropy_init import *

# ----------------------------------------------------------------------------

# Enforce Python version check during package import.
# This is the same check as the one at the top of setup.py
__minimum_python_version__ = "3.6"


class UnsupportedPythonError(Exception):
    pass


if sys.version_info < tuple((int(val) for val in __minimum_python_version__.split('.'))):
    raise UnsupportedPythonError(
        "domehunter does not support Python < {}".format(__minimum_python_version__))

if not _ASTROPY_SETUP_:
    # For egg_info test builds to pass, put package imports here.
    pass


class Dome():
    """
    Interface to dome control raspberry pi GPIO.

    To see the gpio pin mapping to the automation HAT see here,
    https://pinout.xyz/pinout/automation_hat
    For infomation on the gpiozero library see here,
    https://gpiozero.readthedocs.io/en/stable/
    """

    def __init__(self, testing=True, *args, **kwargs):
        """Initialize raspberry pi GPIO environment."""
        if testing:
            # Set the default pin factory to a mock factory
            Device.pin_factory = MockFactory()

            ENCODER_PIN_NUMBER = 26
            # input 2 on the automation hat
            HOME_SENSOR_PIN_NUMBER = 20
            # relay 1 on automation hat
            ROTATION_RELAY_PIN_NUMBER = 13
            # relay 2 on automation hat
            # on position for CW and off for CCW?
            DIRECTION_RELAY_PIN_NUMBER = 19
            # NB I'm just going to move this entirely into a tests file
            # to create test device just do the following
            """
            encoder = DigitialInputDevice(ENCODER_PIN_NUMBER, bounce_time=0.1)
            # create reference to the mock pin used by the device
            encoder_pin = Device.pin_factory.pin(ENCODER_PIN_NUMBER)
            # then toggle the pin high/low to simulate encoder ticks/home home
            # sensor or activation of the relays.
            encoder_pin.drive_low()
            time.sleep(0.1)
            encoder_pin.drive_high()
            """
        else:
            """ Do not change until you're sure!!! """
            # https://pinout.xyz/pinout/automation_hat
            # input 1 on automation hat
            ENCODER_PIN_NUMBER = 26
            # input 2 on the automation hat
            HOME_SENSOR_PIN_NUMBER = 20
            # relay 1 on automation hat
            ROTATION_RELAY_PIN_NUMBER = 13
            # relay 2 on automation hat
            # on position for CW and off for CCW?
            DIRECTION_RELAY_PIN_NUMBER = 19

        # initialize status and az as unknown, to ensure we have properly
        # calibrated az
        self.dome_status = "unknown"
        self.dome_az = None

        # create a instance variable to track the dome motor encoder ticks
        self.encoder_count = 0
        # bounce_time settings gives the time in seconds that the device will
        # ignore additional activation signals
        self.encoder = DigitalInputDevice(ENCODER_PIN_NUMBER, bounce_time=0.1)
        # _increment_count function to run when encoder is triggered
        self.encoder.when_activated = self._increment_count
        # dummy value
        self.az_per_tick = 1

        self._at_home = False
        self.home_sensor = DigitalInputDevice(
            HOME_SENSOR_PIN_NUMBER, bounce_time=0.1)
        # _set_not_home function is run when upon home senser deactivation
        self.home_sensor.when_deactivated = self._set_not_home
        # _set_at_home function is run when home sensor is activated
        self.home_sensor.when_activated = self._set_at_home

        # these two DODs control the relays that control the dome motor
        # the rotation relay is the on/off switch for dome rotation
        # the direction relay will toggle either the CW or CCW direction
        # (using both the normally open and normally close relay terminals)\
        # so when moving the dome, first set the direction relay position
        # then activate the rotation relay
        self.rotation_relay = DigitalOutputDevice(
            ROTATION_RELAY_PIN_NUMBER, initial_value=False)
        self.direction_relay = DigitalOutputDevice(
            DIRECTION_RELAY_PIN_NUMBER, initial_value=False)

###############################################################################
# Properties
###############################################################################

    @property
    def is_home(self):
        """Send True if the dome is at home."""
        return self._at_home

    @property
    def status(self):
        """Return a text string describing dome rotators current status."""
        pass

###############################################################################
# Methods
###############################################################################

    """These map directly onto the AbstractMethods created by RPC."""

    def abort(self):
        """Stop everything."""
        # this could simply call the self._stop_moving() method?
        pass

    def getAz(self):
        """Return AZ."""
        if self.dome_az is None:
            self.calibrate()
        return self.dome_az

    def GotoAz(self, az):
        "Send Dome to Az."
        if self.dome_az is None:
            self.calibrate()
        delta_az = az - self.dome_az
        if abs(delta_az) > 180:
            if delta_az > 0:
                delta_az -= 360
            else:
                delta_az += 360

        if delta_az > 0:
            ticks = self._az_to_ticks(delta_az)
            target_position = self.encoder_count + ticks
            self._move_cw()
            while self.encoder_count <= target_position:
                pass
            self._stop_moving()
            # compare original count to current just in case we got more ticks
            # than we asked for
            old_encoder_count = target_position - ticks
            self.dome_az += self._ticks_to_az(
                self.encoder_count - old_encoder_count)
            self.dome_az %= 360
            self.encoder_count = self._az_to_ticks(self.dome_az)
            pass
        if delta_az < 0:
            # here ticks is going to be negative
            ticks = self._az_to_ticks(delta_az)
            target_position = self.encoder_count + ticks
            self._move_ccw()
            while self.encoder_count >= target_position:
                pass
            self._stop_moving()
            # compare original count to current, just in case we got more ticks
            # than we asked for

            old_encoder_count = target_position - ticks
            self.dome_az += self._ticks_to_az(
                self.encoder_count - old_encoder_count)
            self.dome_az %= 360
            self.encoder_count = self._az_to_ticks(self.dome_az)
            pass
        pass

    def calibrate(self):
        """Calibrate the encoder (determine degrees per tick)"""
        self._move_cw()
        self.home_sensor.wait_for_active()
        time.sleep(0.5)
        self._stop_moving()
        self.encoder_count = 0
        time.sleep(0.5)
        self._move_cw()
        # might be dumb but trying to get two rotations worth of encoder ticks
        self.home_sensor.wait_for_active()
        time.sleep(0.5)
        self._stop_moving()
        time.sleep(0.5)
        self._move_cw()
        self.home_sensor.wait_for_active()
        time.sleep(0.5)
        self._stop_moving()
        self.az_per_tick = 360 / (self.encoder_count / 2)
        pass

    # This will be dome the gRPC python server implementation, which will
    # create an instance of this dome class
    #
    # def start_daemon(self):
    #     """Maybe start the RCP daemon here?."""
    #     raise NotImplementedError
    #
    # def halt_daemon(self):
    #     """Maybe start the RCP daemon here?."""
    #     raise NotImplementedError

###############################################################################
# Private Methods
###############################################################################

    def _set_at_home(self):
        self._at_home = True

    def _set_not_home(self):
        self._at_home = False

    def _increment_count(self, device=None):
        # Unsure what purpose the device variable is supposed to serve here?
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

    def _az_to_ticks(self, az):
        return az / self.az_per_tick

    def _ticks_to_az(self, ticks):
        return ticks * self.az_per_tick

    def _move_cw(self):
        # print(f"Sending GPIO move_cw({degrees}) command.")
        self.current_direction = "CW"
        # set the direction relay switch to CW position
        self.direction_relay.on()
        # turn on rotation
        self.rotation_relay.on()
        cmd_status = True
        return cmd_status

    def _move_ccw(self):
        # print(f"Sending GPIO move_ccw({degrees}) command.")
        self.current_direction = "CCW"
        # set the direction relay switch to CCW position
        self.direction_relay.off()
        # turn on rotation
        self.rotation_relay.on()
        cmd_status = True
        return cmd_status

    def _stop_moving(self):
        self.rotation_relay.off()
        self.last_direction = self.current_direction
        self.current_direction = None
