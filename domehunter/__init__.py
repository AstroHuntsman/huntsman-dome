"""Run dome control on a raspberry pi GPIO."""

# Licensed under a 3-clause BSD style license - see LICENSE.rst
# should keep this content at the top.
# ----------------------------------------------------------------------------
import sys
import time

from gpiozero import Device, DigitalInputDevice, DigitalOutputDevice
from gpiozero.pins.mock import MockFactory
# if we want to use the automation hat status lights we need to
# import the pimoroni led driver
import sn3218
sn3218.disable()
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

    def __init__(self, testing=True, debug_lights=False, *args, **kwargs):
        """Initialize raspberry pi GPIO environment."""
        if testing:
            # Set the default pin factory to a mock factory
            Device.pin_factory = MockFactory()
            # input 1 on automation hat
            ENCODER_PIN_NUMBER = 26
            # input 2 on the automation hat
            HOME_SENSOR_PIN_NUMBER = 20
            # relay 1 on automation hat
            ROTATION_RELAY_PIN_NUMBER = 13
            # relay 2 on automation hat
            # on position for CW and off for CCW?
            DIRECTION_RELAY_PIN_NUMBER = 19
            # set a timeout length in seconds for wait_for_active() calls
            WAIT_TIMEOUT = 1
            # set a variable for bounce_time in seconds
            BOUNCE_TIME = 0.1

            self.encoder_pin = Device.pin_factory.pin(ENCODER_PIN_NUMBER)
            self.home_sensor_pin = Device.pin_factory.pin(HOME_SENSOR_PIN_NUMBER)
        else:
            """ Do not change until you're sure!!! """
            # input 1 on automation hat
            ENCODER_PIN_NUMBER = 26
            # input 2 on the automation hat
            HOME_SENSOR_PIN_NUMBER = 20
            # relay 1 on automation hat
            ROTATION_RELAY_PIN_NUMBER = 13
            # relay 2 on automation hat
            # no position for CW and nc for CCW?
            DIRECTION_RELAY_PIN_NUMBER = 19
            # set the timeout length variable to None for non testing mode
            WAIT_TIMEOUT = None
            # set a variable for bounce_time in seconds
            BOUNCE_TIME = 0.1

        if debug_lights:
            sn3218.enable()
            self.led_lights_id = {
                                    'power': 0b100000000000000000,
                                    'comms': 0b010000000000000000,
                                    'warn': 0b001000000000000000,
                                    'input_1': 0b000100000000000000,
                                    'input_2': 0b000010000000000000,
                                    'input_3': 0b000001000000000000,
                                    'relay_3_nc': 0b000000100000000000,
                                    'relay_3_no': 0b000000010000000000,
                                    'relay_2_nc': 0b000000001000000000,
                                    'relay_2_no': 0b000000000100000000,
                                    'relay_1_nc': 0b000000000010000000,
                                    'relay_1_no': 0b000000000001000000,
                                    'output_3': 0b000000000000100000,
                                    'output_2': 0b000000000000010000,
                                    'output_1': 0b000000000000001000,
                                    'adc_3': 0b000000000000000100,
                                    'adc_2': 0b000000000000000010,
                                    'adc_1': 0b000000000000000001
                                 }
            # led_status is binary number, each zero/position sets the state
            # of an LED, where 0 is off and 1 is on
            self.led_status = 0b000000000000000000
            sn3218.enable_leds(self.led_status)
        # initialize status and az as unknown, to ensure we have properly
        # calibrated az
        self.testing = testing
        self.debug_lights = debug_lights
        self.dome_status = "unknown"
        self.dome_az = None


        # create a instance variable to track the dome motor encoder ticks
        self.encoder_count = 0
        # bounce_time settings gives the time in seconds that the device will
        # ignore additional activation signals
        self.encoder = DigitalInputDevice(
            ENCODER_PIN_NUMBER, bounce_time=BOUNCE_TIME)
        # _increment_count function to run when encoder is triggered
        self.encoder.when_activated = self._increment_count
        # dummy value
        self.az_per_tick = 1

        self._at_home = False
        self.home_sensor = DigitalInputDevice(
            HOME_SENSOR_PIN_NUMBER, bounce_time=BOUNCE_TIME)
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
        # because we initiliase the relay in the nc position
        self.current_direction = "CCW"
        if debug_lights:
            self._turn_led_on(leds=['relay_2_nc'])
            self._turn_led_on(leds=['relay_1_nc'])

        # set a wait time for testing mode that exceeds BOUNCE_TIME
        self.t_wait = BOUNCE_TIME + 0.05
        # set the timeout for wait_for_active()
        self.wait_timeout = WAIT_TIMEOUT

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
        self._stop_moving()
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

        # determine whether CW or CCW gives the short path to desired az
        if abs(delta_az) > 180:
            if delta_az > 0:
                delta_az -= 360
            else:
                delta_az += 360

        # if updated delta_az is positive, direction is CW
        if delta_az > 0:
            # converted delta_az to equivilant in encoder ticks
            ticks = self._az_to_ticks(delta_az)
            target_position = self.encoder_count + ticks
            self._move_cw()
            # wait until encoder count matches desired delta az
            while self.encoder_count < target_position:
                if self.testing:
                    # if testing simulate a tick for every cycle of while loop
                    self._simulate_ticks(num_ticks=1)
                pass
            self._stop_moving()
            # compare original count to current just in case we got more ticks
            # than we asked for
            old_encoder_count = target_position - ticks
            # update dome_az based on the actual number of ticks counted
            self.dome_az += self._ticks_to_az(
                self.encoder_count - old_encoder_count)
            # take mod360 of dome_az to keep 0 <= dome_az < 360
            self.dome_az %= 360
            # update encoder_count to match the dome_az
            self.encoder_count = self._az_to_ticks(self.dome_az)
            pass

        # if updated delta_az is negative, direction is CCW
        if delta_az < 0:
            # converted delta_az to equivilant in encoder ticks
            ticks = self._az_to_ticks(delta_az)
            target_position = self.encoder_count + ticks
            self._move_ccw()
            # wait until encoder count matches desired delta az
            while self.encoder_count >= target_position:
                if self.testing:
                    # if testing simulate a tick for every cycle of while loop
                    self._simulate_ticks(num_ticks=1)
                pass
            self._stop_moving()
            # compare original count to current, just in case we got more ticks
            # than we asked for
            old_encoder_count = target_position - ticks
            # update dome_az based on the actual number of ticks counted
            self.dome_az += self._ticks_to_az(
                self.encoder_count - old_encoder_count)
            # take mod360 of dome_az to keep 0 <= dome_az < 360
            self.dome_az %= 360
            # update encoder_count to match the dome_az
            self.encoder_count = self._az_to_ticks(self.dome_az)
            pass
        pass

    def calibrate(self, num_cal_rotations=2):
        """Calibrate the encoder (determine degrees per tick)"""
        # rotate the dome until we hit home, to give reference point
        self._move_cw()
        self.home_sensor.wait_for_active(timeout=self.wait_timeout)
        if self.testing:
            self.home_sensor_pin.drive_high()
        time.sleep(0.1)
        self._stop_moving()
        self.encoder_count = 0

        # now set dome to rotate n times so we can determine the number of
        # ticks per revolution
        rotation_count = 0
        while rotation_count < num_cal_rotations:
            time.sleep(0.5)
            self._move_cw()
            if self.testing:
                self.home_sensor_pin.drive_low()
                self._simulate_ticks(num_ticks=10)
            self.home_sensor.wait_for_active(timeout=self.wait_timeout)
            if self.testing:
                self.home_sensor_pin.drive_high()
            time.sleep(0.5)
            self._stop_moving()

            rotation_count += 1

        self.az_per_tick = 360 / (self.encoder_count / rotation_count)
        pass

###############################################################################
# Private Methods
###############################################################################

    def _set_at_home(self):
        self._turn_led_on(leds=['input_2'])
        self._at_home = True

    def _set_not_home(self):
        self._turn_led_off(leds=['input_2'])
        self._at_home = False

    def _increment_count(self):
        # Unsure what purpose the device variable is supposed to serve here?
        print(f"Encoder activated _increment_count")
        self._turn_led_on(leds=['input_1'])
        time.sleep(0.01)
        self._turn_led_off(leds=['input_1'])
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
        if self.testing and self._at_home:
            self.home_sensor_pin.drive_low()
        self.last_direction = self.current_direction
        self.current_direction = "CW"
        # set the direction relay switch to CW position
        self.direction_relay.on()
        if self.last_direction == "CCW":
            self._turn_led_off(leds=['relay_2_nc'])
        self._turn_led_on(leds=['relay_2_no'])
        # turn on rotation
        self.rotation_relay.on()
        self._turn_led_on(leds=['relay_1_no'])
        self._turn_led_off(leds=['relay_1_nc'])
        cmd_status = True
        return cmd_status

    def _move_ccw(self):
        if self.testing and self._at_home:
            self.home_sensor_pin.drive_low()
        self.last_direction = self.current_direction
        self.current_direction = "CCW"
        # set the direction relay switch to CCW position
        self.direction_relay.off()
        if self.last_direction == "CW":
            self._turn_led_off(leds=['relay_2_no'])
        self._turn_led_on(leds=['relay_2_nc'])
        # turn on rotation
        self.rotation_relay.on()
        self._turn_led_on(leds=['relay_1_no'])
        self._turn_led_off(leds=['relay_1_nc'])
        cmd_status = True
        return cmd_status

    def _stop_moving(self):
        self.rotation_relay.off()
        self._turn_led_off(leds=['relay_1_no'])
        self._turn_led_on(leds=['relay_1_nc'])
        self.last_direction = self.current_direction

    def _simulate_ticks(self, num_ticks):
        tick_count = 0
        while tick_count < num_ticks:
            self.encoder_pin.drive_low()
            time.sleep(self.t_wait)
            self.encoder_pin.drive_high()
            time.sleep(self.t_wait)
            tick_count += 1

    def _turn_led_on(self, leds=[]):
        # pass a list of strings of the leds to turn on
        if self.debug_lights:
            for led in leds:
                self.led_status |= self.led_lights_id[led]
            sn3218.enable_leds(self.led_status)
        pass

    def _turn_led_off(self, leds=[]):
        # pass a list of strings of the leds to turn off
        # note: need something to prevent us turning an LED off/on more than
        # once in a row because it will affect the binary led_status in
        # unintended ways
        if self.debug_lights:
            for led in leds:
                self.led_status ^= self.led_lights_id[led]
            sn3218.enable_leds(self.led_status)
        pass
