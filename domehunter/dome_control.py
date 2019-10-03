"""Run dome control on a raspberry pi GPIO."""


import math
import sys
import time
import warnings

import astropy.units as u
from astropy.coordinates import Longitude
from gpiozero import Device, DigitalInputDevice, DigitalOutputDevice
from gpiozero.pins.mock import MockFactory

from domehunter.enumerations import Direction, LED_light, ReturnCode

from ._astropy_init import *

# if we want to use the automation hat status lights we need to
# import the pimoroni led driver
try:  # pragma: no cover
    import sn3218
    sn3218.disable()
except OSError:  # pragma: no cover
    wmsg = ("AutomationHAT hardware not detected, "
            "testing=True and debug_lights=False recommended.")
    warnings.warn(wmsg)
except Exception:  # pragma: no cover
    wmsg = ("Something went wrong in importing sn3218, "
            "status lights unlikely to work.")
    warnings.warn(wmsg)


# ----------------------------------------------------------------------------


# TODO: set up functions to raise custom exceptions to allow server to
#       properly handle exceptions
class DomeCommandError(Exception):  # pragma: no cover
    # generic dome command error, placeholder for now
    pass


class Dome(object):
    """
    Interface to dome control raspberry pi GPIO.

    This is a class object that represents the observatory dome. It tracks the
    Dome azimuth using an encoder attached to the dome motor and a home sensor
    that provides a reference azimuth position.

    The Dome class is initialised and run on a system consisting of a Raspberry
    Pi and a Pimoroni AutomationHAT. If an AutomationHAT is not available, the
    code can be run on an ordinary system in testing mode with the debug_lights
    option disabled.

    To see the gpio pin mapping to the automation HAT see here,
    https://pinout.xyz/pinout/automation_hat
    For infomation on the gpiozero library see here,
    https://gpiozero.readthedocs.io/en/stable/
    """

    def __init__(self,
                 testing=True,
                 debug_lights=False,
                 home_azimuth=0.0,
                 az_position_tolerance=1.0,
                 degrees_per_tick=1.0,
                 encoder_pin_number=26,
                 home_sensor_pin_number=20,
                 rotation_relay_pin_number=13,
                 direction_relay_pin_number=19,
                 bounce_time=0.1,
                 *args,
                 **kwargs):
        """
        Initialize raspberry pi GPIO environment.

        Default settings are to run in testing mode, where we create some mock
        hardware using the GPIOzero library. Otherwise the GPIOzero library
        will automatically detect the GPIO pins of the Rasberry Pi when
        'testing=False'. With 'debug_lights=True', LEDs on AutomationHat will
        be used to indicate current state.

        Next the GIPO pins must be mapped to the correct sensor (e.g. home
        sensor) they are attached to on the automationHAT that we want to make
        use of. See here for reference,
        https://pinout.xyz/pinout/automation_hat

        Once the necessary pin numbers have been identified we can set about
        creating GPIOzero objects to make use of the automationHat. This
        includes,
        - A digital input device for the encoder (`encoder_pin_number`)
        - A digital input device for the home sensor (`home_sensor_pin_number`)
        - A digital output device for the motor on/off relay switch
          (`rotation_relay_pin_number`)
        - A digital output device for the motor direction (CW/CCW) relay switch
          (`direction_relay_pin_number`)

        The Digital Input Devices (DIDs) have callback functions that can be
        used to call a function upon activation or deactivation  of a sensor
        via a GPIO. For example, activating the encoder DID can be set to
        increment a Dome encoder count instance variable.

        As part of initialisation several instance variables will be set to
        designate status infomation about the dome such as dome azimuth
        (unknown at initialisation) and position of the direction relay switch
        (initialised in the CCW position).

        Parameters
        ----------
        testing : boolean
            Toggle to enable a simulated hardware testing mode.
        debug_lights : boolean
            Toggle to enable the status LEDs on the automationHAT.
        home_azimuth: float
            The home azimuth position in degrees (integer between 0 and 360).
            Defaults to 0.
        az_position_tolerance: float
            The tolerance used during GotoAz() calls. Dome will move to
            requested position to within this tolerance. If the calibrated
            degrees_per_tick is greater than az_position_tolerance,
            degrees_per_tick will be used as the tolerance instead.
        degrees_per_tick: float
            The calibrated number of degrees (azimuth) per encoder tick.
        encoder_pin_number : int
            The GPIO pin that corresponds to the encoder input on the
            automationHAT (input 1).
        home_sensor_pin_number : int
            The GPIO pin that corresponds to the home input on the
            automationHAT (input 2).
        rotation_relay_pin_number : int
            The GPIO pin that corresponds to the rotation relay on the
            automationHAT (relay 1). The normally open terminal on the
            rotation relay is connected to the common terminal of the direction
            relay.
        direction_relay_pin_number : int
            The GPIO pin that corresponds to the direction relay on the
            automationHAT (relay 2). The Normally Open (NO) relay position
            corresponds to clockwise (CW) and the Normally Closed (NC)
            position corresponds to counterclockwise (CCW).
        bounce_time : float
            A buffer period (in seconds) where home/encoder input will ignore
            additional (de)activation.

        """

        if testing:
            # Set the default pin factory to a mock factory
            Device.pin_factory = MockFactory()
            # in case a previous instance has been initialised, tell the
            # pin factory to release all the pins
            Device.pin_factory.reset()
            # set a timeout length in seconds for wait_for_active() calls
            WAIT_TIMEOUT = 1

            # in testing mode we need to create a seperate pin object so we can
            # simulate the activation of our fake DIDs and DODs
            self._encoder_pin = Device.pin_factory.pin(encoder_pin_number)
            self._home_sensor_pin = Device.pin_factory.pin(
                home_sensor_pin_number)
        else:
            # set the timeout length variable to 5 minutes (units of seconds)
            WAIT_TIMEOUT = 5 * 60

        # set a wait time for testing mode that exceeds bounce_time
        self.test_mode_delay_duration = bounce_time + 0.05
        # set the timeout for wait_for_active()
        self.wait_timeout = WAIT_TIMEOUT

        self.testing = testing
        self.debug_lights = debug_lights
        # TODO: read in default value from yaml(?)
        self._degrees_per_tick = degrees_per_tick
        self.az_position_tolerance = az_position_tolerance
        # if the requested tolerance is less than degrees_per_tick use
        # degrees_per_tick for the tolerance
        self.az_position_tolerance = max(
            self.az_position_tolerance, self.degrees_per_tick)
        self.home_az = Longitude(home_azimuth * u.deg)
        # need something to let us know when dome is calibrating so home sensor
        # activation doesnt zero encoder counts
        self.calibrating = False

        # NOTE: this led setup needs to be done before setting any callback
        # functions
        # turn on the relay LEDs if we are debugging
        # led_status is set with binary number, each zero/position sets the
        # state of an LED, where 0 is off and 1 is on
        self.led_status = LED_Lights.RELAY_1_NO | LED_Lights.RELAY_2_NO
        # the initial led_status is set to indicate the positions the relays
        # are initialised in (normally closed)
        # use the LED_lights enum.Flag class to pass binary integers masks to
        # the _change_led_state() method.
        if debug_lights:  # pragma: no cover
            # if we are actually using the debug lights we can enable them now
            self._change_led_state(1,
                                   leds=[LED_light.RELAY_1_NC,
                                         LED_light.RELAY_2_NC])
            sn3218.enable_leds(self.led_status)
            sn3218.enable()

        # create a instance variable to track the dome motor encoder ticks
        self._encoder_count = 0
        # bounce_time settings gives the time in seconds that the device will
        # ignore additional activation signals
        self._encoder = DigitalInputDevice(
            encoder_pin_number, bounce_time=bounce_time)
        # _increment_count function to run when encoder is triggered
        self._encoder.when_activated = self._increment_count
        self._encoder.when_deactivated = self.self._turn_off_input_1_led

        self._home_sensor = DigitalInputDevice(
            home_sensor_pin_number, bounce_time=bounce_time)
        if self._home_sensor.is_active:
            self._set_at_home()
        else:
            self._set_not_home()
        # _set_not_home function is run when upon home senser deactivation
        self._home_sensor.when_deactivated = self._set_not_home
        # _set_at_home function is run when home sensor is activated
        self._home_sensor.when_activated = self._set_at_home

        # these two DODs control the relays that control the dome motor
        # the rotation relay is the on/off switch for dome rotation
        # the direction relay will toggle either the CW or CCW direction
        # (using both the normally open and normally close relay terminals)
        # so when moving the dome, first set the direction relay position
        # then activate the rotation relay
        self._rotation_relay = DigitalOutputDevice(
            rotation_relay_pin_number, initial_value=False)
        self._direction_relay = DigitalOutputDevice(
            direction_relay_pin_number, initial_value=False)
        # because we initialiase the relay in the normally closed position
        self.current_direction = Direction.CCW


###############################################################################
# Properties
###############################################################################

    @property
    def dome_az(self):
        """ """
        return self._ticks_to_az(self._encoder_count)

    @property
    def at_home(self):
        """Send True if the dome is at home."""
        return self._home_sensor.is_active

    @property
    def dome_in_motion(self):
        """Send True if dome is in motion."""
        return self._rotation_relay.is_active

    @property
    def encoder_count(self):
        """Returns the current encoder count."""
        return self._encoder_count

    @property
    def degrees_per_tick(self):
        """Returns the calibrated azimuth (in degrees) per encoder tick."""
        return self._degrees_per_tick
###############################################################################
# Methods
###############################################################################

    """These map directly onto the AbstractMethods created by RPC."""

    def abort(self):
        """
        Stop everything by switching the dome motor on/off relay to off.

        """
        # TODO: consider another way to do this in case the relay fails/sticks
        # one way might be cut power to the automationHAT so the motor relays
        # will receive no voltage even if the relay is in the open position?
        self._stop_moving()

    def getAz(self):
        """
        Return current Azimuth of the Dome.

        Returns
        -------
        float
            The Dome azimuth in degrees.

        """
        # TODO: Now that dome_az is a property calculated from encoder_count
        # it is no longer initialised as None, so instead probably need some
        # other form of error/exception handling here (if encoder_count is
        # None?)
        if self.dome_az is None:
            print("Cannot return Azimuth as Dome is not yet calibrated.\
                   Run calibration loop")
            return self.dome_az
        return self.dome_az.degree

    def GotoAz(self, az):
        """
        Send Dome to a requested Azimuth position.

        Parameters
        ----------
        az : float
            Desired dome azimuth position in degrees.

        """
        if self.dome_az is None:
            print("Dome Azimuth unknown, please manually trigger, \
                  calibration from TheSkyX.")
            return

        target_az = Longitude(az * u.deg)
        # calculate delta_az, wrapping at 180 to ensure we take shortest route
        delta_az = (target_az - self.dome_az).wrap_at(180 * u.degree)

        if delta_az > 0:
            self._rotate_dome(Direction.CW)
        else:
            self._rotate_dome(Direction.CCW)
        # wait until encoder count matches desired delta az
        while (target_az - self.dome_az).wrap_at(180 * u.degree) > self.az_position_tolerance:
            if self.testing:
                # if testing simulate a tick for every cycle of while loop
                self._simulate_ticks(num_ticks=1)
            else:
                # micro break to spare the little rpi cpu
                time.sleep(0.1)
        self._stop_moving()

    def calibrate_dome_encoder_counts(self, num_cal_rotations=2):
        """
        Calibrate the encoder (determine degrees per tick).

        Parameters
        ----------
        num_cal_rotations : integer
            Number of rotations to perform to calibrate encoder.

        """
        # rotate the dome until we hit home, to give reference point
        self.find_home()

        # pause to let things settle/get a noticeable blink of debug_lights
        time.sleep(0.5)

        rotation_count = 0
        self.calibrating = True
        # now set dome to rotate num_cal_rotations times so we can determine
        # the number of ticks per revolution
        while rotation_count < num_cal_rotations:
            self._rotate_dome(Direction.CW)
            if self.testing:
                # tell the fake home sensor that we have left home
                self._home_sensor_pin.drive_low()
                self._simulate_ticks(num_ticks=10)
            self._home_sensor.wait_for_inactive(timeout=self.wait_timeout)
            self._home_sensor.wait_for_active(timeout=self.wait_timeout)

            if self.testing:
                # tell the fake home sensor that we have come back to home
                time.sleep(0.1)
                self._home_sensor_pin.drive_high()
                time.sleep(0.1)

            # without this pause the wait_for_active wasn't waiting (???)
            time.sleep(0.1)

            rotation_count += 1

        self._stop_moving()

        # set the azimuth per encoder tick factor based on how many ticks we
        # counted over n rotations
        self._degrees_per_tick = 360 / (self.encoder_count / rotation_count)
        # update the az_position_tolerance
        self.az_position_tolerance = max(
            self.az_position_tolerance, self.degrees_per_tick)
        self.calibrating = False

    def find_home(self):
        """
        Move Dome to home position.

        """
        self._rotate_dome(Direction.CW)
        time.sleep(0.1)
        self._home_sensor.wait_for_active(timeout=self.wait_timeout)
        if self.testing:
            # in testing mode need to "fake" the activation of the home pin
            time.sleep(0.5)
            self._home_sensor_pin.drive_high()

        self._stop_moving()

    def sync(self, az):
        self._encoder_count = self._az_to_ticks(Longitude(az * u.deg))
        return

###############################################################################
# Private Methods
###############################################################################

    def _set_at_home(self):
        """
        Update home status to at home and debug LEDs (if enabled).
        """
        self._change_led_state(1, leds=[LED_light.INPUT_2])
        # don't want to zero encoder while calibrating
        # note: because Direction.CW is +1 and Direction.CCW is -1, need to
        # add 1 to self.direction in order to get CCW to evaluate to False
        if not self.calibrating and bool(self.direction + 1):
            self._encoder_count = 0

    def _set_not_home(self):
        """
        Update home status to not at home and debug LEDs (if enabled).
        """
        self._change_led_state(0, leds=[LED_light.INPUT_2])

    def _increment_count(self):
        """
        Private method used for callback function of the encoder DOD.

        Calling this method will toggle the encoder debug LED (if enabled)
        and increment or decrement the encoder_count instance variable,
        depending on the current rotation direction of the dome.

        If the current dome direction cannot be determined, the last recorded
        direction is adopted.
        """
        print(f"Encoder activated _increment_count")
        self._change_led_state(1, leds=[LED_light.INPUT_1])

        if self.current_direction != Direction.NONE:
            self._encoder_count += self.current_direction
        elif self.last_direction != Direction.NONE:
            self._encoder_count += self.last_direction
        else:
            raise RuntimeError("Oh no.")

    def _az_to_ticks(self, az):
        """
        Convert degrees (azimuth) to equivalent in encoder tick count. Because
        we zero the encoder at the home position, this conversion needs to
        take into account the offset between the zero azimuth position and the
        zero encoder position.

        Parameters
        ----------
        az : astropy.coordinates.Longitude
            Dome azimuth position in degrees.

        Returns
        -------
        float
            Returns encoder tick count corresponding to dome azimuth.

        """
        az_relative_to_home = (az - self.home_az).wrap_at(360 * u.degree)
        return az_relative_to_home.degree / self.degrees_per_tick

    def _ticks_to_az(self, ticks):
        """
        Convert encoder tick count to equivalent in degrees (azimuth).

        Parameters
        ----------
        ticks : integer
            The number of encoder ticks recorded.

        Returns
        -------
        astropy.coordinates.longitude
            The corresponding dome azimuth position in degrees.

        """
        tick_to_deg = Longitude(ticks * self.degrees_per_tick * u.deg)
        return Longitude(self.home_az + tick_to_deg)

    def _rotate_dome(self, direction):
        """
        Set dome to move clockwise.

        Returns
        -------
        integer
            Command status return code (tbd).

        """
        # if testing, deactivate the home_sernsor_pin to simulate leaving home
        if self.testing and self.at_home:
            self._home_sensor_pin.drive_low()
        # update the last_direction instance variable
        self.last_direction = self.current_direction
        # now update the current_direction variable to CW
        self.current_direction = direction
        # set the direction relay switch to CW position
        if self.current_direction == Direction.CW:
            self._direction_relay.on()
            self._change_led_state(1, leds=[LED_light.RELAY_2_NO])
            self._change_led_state(0, leds=[LED_light.RELAY_2_NC])
        elif self.current_direction.name == Direction.CCW:
            self._direction_relay.off()
            self._change_led_state(0, leds=[LED_light.RELAY_2_NO])
            self._change_led_state(1, leds=[LED_light.RELAY_2_NC])
        # turn on rotation
        self._rotation_relay.on()
        # update the rotation relay debug LEDs
        self._change_led_state(1, leds=[LED_light.RELAY_1_NO])
        self._change_led_state(0, leds=[LED_light.RELAY_1_NC])
        cmd_status = True
        return cmd_status

    def _stop_moving(self):
        """
        Stop dome movement by switching the dome rotation relay off.
        """
        self._rotation_relay.off()
        # update the debug LEDs
        self._change_led_state(0, leds=[LED_light.RELAY_1_NO])
        self._change_led_state(1, leds=[LED_light.RELAY_1_NC])
        # update last_direction with current_direction at time of method call
        self.last_direction = self.current_direction
        self.current_direction = Direction.NONE

    def _simulate_ticks(self, num_ticks):
        """
        Method to simulate encoder ticks while in testing mode.
        """
        # repeat this loop of driving the mock pins low then high to simulate
        # an encoder tick. Continue until desired number of ticks is reached.
        for tick_count in range(num_ticks):
            self._encoder_pin.drive_low()
            # test_mode_delay_duration is set so that it will always exceed
            # the set bounce_time
            # of the pins
            time.sleep(self.test_mode_delay_duration)
            self._encoder_pin.drive_high()
            time.sleep(self.test_mode_delay_duration)

    def _change_led_state(self, desired_state, leds=[]):  # pragma: no cover
        """
        Method of turning a set of debugging LEDs on

        Parameters
        ----------
        desired_state : bool
            Parameter to indicate whether leds are being turned on (1 or True)
            or if they are being turned off (0 or False).
        leds : list
            List of LED_light enums to indicate which LEDs to turn on.

        """
        # pass a list of strings of the leds to turn on
        if not(self.debug_lights):
            return
        if leds == []:
            # if leds is an empty list do nothing
            return None

        for led in leds:
            if desired_state is 1:
                self.led_status |= led
            elif desired_state is 0:
                self.led_status &= ~led
        # pass the new binary int to LED controller
        sn3218.enable_leds(self.led_status)

    def self._turn_off_input_1_led(self):
        self._change_led_state(0, leds=[LED_light.INPUT_1])
