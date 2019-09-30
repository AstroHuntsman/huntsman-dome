"""Run dome control on a raspberry pi GPIO."""


import math
import sys
import time
import warnings

from enum import Enum
import astropy.units as u
from astropy.coordinates import Longitude
from gpiozero import Device, DigitalInputDevice, DigitalOutputDevice
from gpiozero.pins.mock import MockFactory

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


class LED_light(Flag):
    POWER = 0b100000000000000000
    COMMS = 0b010000000000000000
    WARN = 0b001000000000000000
    INPUT_1 = 0b000100000000000000
    INPUT_2 = 0b000010000000000000
    INPUT_3 = 0b000001000000000000
    RELAY_3_NC = 0b000000100000000000
    RELAY_3_NO = 0b000000010000000000
    RELAY_2_NC = 0b000000001000000000
    RELAY_2_NO = 0b000000000100000000
    RELAY_1_NC = 0b000000000010000000
    RELAY_1_NO = 0b000000000001000000
    OUTPUT_3 = 0b000000000000100000
    OUTPUT_2 = 0b000000000000010000
    OUTPUT_1 = 0b000000000000001000
    ADC_3 = 0b000000000000000100
    ADC_2 = 0b000000000000000010
    ADC_1 = 0b000000000000000001


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
                 home_azimuth=0,
                 az_position_tolerance=1.0,
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
        home_azimuth: int
            The home azimuth position in degrees (integer between 0 and 360).
            Defaults to 0.
        az_position_tolerance: int
            The tolerance used during GotoAz() calls. Dome will move to
            requested position to within this tolerance. If the calibrated
            az_per_tick is greater than az_position_tolerance, az_per_tick will
            be used as the tolerance instead.
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
        direction_cw_relay_pin_number : int
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
            self.__encoder_pin = Device.pin_factory.pin(encoder_pin_number)
            self.__home_sensor_pin = Device.pin_factory.pin(
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
        # set the desired home_az
        self.az_position_tolerance = az_position_tolerance
        self.home_az = Longitude(home_azimuth * u.deg)
        # need something to let us know when dome is calibrating so home sensor
        # activation doesnt zero encoder counts
        self.calibrating = False

        # create a instance variable to track the dome motor encoder ticks
        self.__encoder_count = 0
        # bounce_time settings gives the time in seconds that the device will
        # ignore additional activation signals
        self.__encoder = DigitalInputDevice(
            encoder_pin_number, bounce_time=bounce_time)
        # _increment_count function to run when encoder is triggered
        self.__encoder.when_activated = self._increment_count
        self.__encoder.when_deactivated = self._turn_led_off(
            leds=[LED_light.INPUT_1])
        # set dummy value initially to force a rotation calibration run
        self.__az_per_tick = None

        self._set_not_home()
        self.__home_sensor = DigitalInputDevice(
            home_sensor_pin_number, bounce_time=bounce_time)
        # _set_not_home function is run when upon home senser deactivation
        self.__home_sensor.when_deactivated = self._set_not_home
        # _set_at_home function is run when home sensor is activated
        self.__home_sensor.when_activated = self._set_at_home

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
        self.current_direction = "CCW"

        # turn on the relay LEDs if we are debugging
        # led_status is set with binary number, each zero/position sets the
        # state of an LED, where 0 is off and 1 is on
        self.led_status = 0b000000001010000000
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


###############################################################################
# Properties
###############################################################################

    @property
    def dome_az(self):
        """ """
        return self._ticks_to_az(self.__encoder_count)

    @property
    def is_home(self):
        """Send True if the dome is at home."""
        return self._at_home

    @property
    def dome_in_motion(self):
        """Send True if dome is in motion."""
        return bool(self._rotation_relay.value)

    @property
    def encoder_count(self):
        """Returns the current encoder count."""
        return self.__encoder_count

    @property
    def az_per_tick(self):
        """Returns the calibrated azimuth (in degrees) per encoder tick."""
        return self.__az_per_tick
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
        # it is no longer initialised a None, so instead probably need some
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
            print('Dome Azimuth unknown, finding Home position,'
                  '- then will go to requested Azimuth position.')
            self.find_home()

        target_az = Longitude(az * u.deg)
        # calculate delta_az, wrapping at 180 to ensure we take shortest route
        delta_az = (target_az - self.dome_az).wrap_at(180 * u.degree)
        # converte delta_az to equivilant in encoder ticks
        ticks = self._az_to_ticks(delta_az)
        target_position = self._ticks_to_az(self.encoder_count + ticks)

        if delta_az > 0:
            self._move_cw()
        else:
            self._move_ccw()
        # if the requested tolerance is less than az_per_tick use az_per_tick
        # for the tolerance
        tolerance = max(self.az_position_tolerance, self.az_per_tick)
        # wait until encoder count matches desired delta az
        while not math.isclose(self.dome_az.degree,
                               target_position.degree,
                               abs_tol=tolerance):
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
            self._move_cw()
            if self.testing:
                # tell the fake home sensor that we have left home
                self.__home_sensor_pin.drive_low()
                self._simulate_ticks(num_ticks=10)
            # need to introduce a small pause before wait_for_active as we
            # start from home position and want to make sure we clear the
            # sensor before we start waiting for it to come around again
            time.sleep(2)
            self.__home_sensor.wait_for_active(timeout=self.wait_timeout)

            if self.testing:
                # tell the fake home sensor that we have come back to home
                time.sleep(0.1)
                self.__home_sensor_pin.drive_high()
                time.sleep(0.1)

            # without this pause the wait_for_active wasn't waiting (???)
            time.sleep(0.1)

            rotation_count += 1

        self._stop_moving()

        # set the azimuth per encoder tick factor based on how many ticks we
        # counted over n rotations
        self.__az_per_tick = 360 / (self.encoder_count / rotation_count)
        self.calibrating = False

    def find_home(self):
        """
        Move Dome to home position.

        """
        self._move_cw()
        time.sleep(0.1)
        self.__home_sensor.wait_for_active(timeout=self.wait_timeout)
        if self.testing:
            # in testing mode need to "fake" the activation of the home pin
            time.sleep(0.5)
            self.__home_sensor_pin.drive_high()

        self._stop_moving()

###############################################################################
# Private Methods
###############################################################################

    def _set_at_home(self):
        """
        Update home status to at home and debug LEDs (if enabled).
        """
        self._change_led_stateon(leds=[LED_light.INPUT_2])
        # don't want to zero encoder while calibrating
        if not self.calibrating:
            self.__encoder_count = 0
        self._at_home = True

    def _set_not_home(self):
        """
        Update home status to not at home and debug LEDs (if enabled).
        """
        self._change_led_state(0, leds=[LED_light.INPUT_2])
        self._at_home = False

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

        if self.current_direction is None:
            self.current_direction = self.last_direction

        if self.current_direction == "CW":
            self.__encoder_count += 1
        elif self.current_direction == "CCW":
            self.__encoder_count -= 1
        # TODO what is last_direction is also None?

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
        return az_relative_to_home.degree / self.az_per_tick

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
        tick_to_deg = Longitude(ticks * self.az_per_tick * u.deg)
        return (self.home_az + tick_to_deg).wrap_at(360 * u.degree)

    def _move_cw(self):
        """
        Set dome to move clockwise.

        Returns
        -------
        integer
            Command status return code (tbd).

        """
        # if testing, deactivate the home_sernsor_pin to simulate leaving home
        if self.testing and self._at_home:
            self.__home_sensor_pin.drive_low()
        # update the last_direction instance variable
        self.last_direction = self.current_direction
        # now update the current_direction variable to CW
        self.current_direction = "CW"
        # set the direction relay switch to CW position
        self._direction_relay.on()
        # update the debug LEDs LED_light.RELAY_1_NC
        if self.last_direction.value:
            self._change_led_state(0, leds=[LED_light.RELAY_2_NC])
        if not self.last_direction.value:
            self._change_led_state(0, leds=[LED_light.RELAY_2_NO])
        if self.current_direction.value:
            self._change_led_state(1, leds=[LED_light.RELAY_2_NO])
        if not self.current_direction.value:
            self._change_led_state(1, leds=[LED_light.RELAY_2_NC])
        # turn on rotation
        self._rotation_relay.on()
        # update the rotation relay debug LEDs
        cmd_status = True
        return cmd_status

    def _move_ccw(self):
        """
        Set dome to move counter-clockwise.

        Returns
        -------
        integer
            Command status return code (tbd).

        """
        # if testing, deactivate the home_sernsor_pin to simulate leaving home
        if self.testing and self._at_home:
            self.__home_sensor_pin.drive_low()
        # update the last_direction instance variable
        self.last_direction = self.current_direction
        # now update the current_direction variable to CCW
        self.current_direction = "CCW"
        # set the direction relay switch to CCW position
        self._direction_relay.off()
        # update the debug LEDs
        if self.last_direction == "CW":
            self._turn_led_off(leds=['relay_2_normally_open'])
        self._turn_led_on(leds=['relay_2_normally_closed'])
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

    def _simulate_ticks(self, num_ticks):
        """
        Method to simulate encoder ticks while in testing mode.
        """
        tick_count = 0
        # repeat this loop of driving the mock pins low then high to simulate
        # an encoder tick. Continue until desired number of ticks is reached.
        while tick_count < num_ticks:
            self.__encoder_pin.drive_low()
            # test_mode_delay_duration is set so that it will always exceed
            # the set bounce_time
            # of the pins
            time.sleep(self.test_mode_delay_duration)
            self.__encoder_pin.drive_high()
            time.sleep(self.test_mode_delay_duration)
            tick_count += 1

    def _change_led_state(self, desired_state, leds=[]):  # pragma: no cover
        """
        Method of turning a set of debugging LEDs on

        Parameters
        ----------
        desired_state : bool
            Parameter to indicate whether leds are being turned on (1 or True)
            or if they are being turned off (0 or False).
        leds : list
            List of LED name string to indicate which LEDs to turn on.

        """
        # pass a list of strings of the leds to turn on
        if not(self.debug_lights):
            return None
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

    def _turn_led_off(self, leds=[]):  # pragma: no cover
        """
        Method of turning a set of debugging LEDs off.

        Parameters
        ----------
        leds : list
            List of LED name string to indicate which LEDs to turn off.

        """
        # pass a list of strings of the leds to turn on
        if not(self.debug_lights):
            return None
        if leds == []:
            # if leds is an empty list do nothing
            return None

        for led in leds:
            self.led_status &= ~led
        # pass the new binary int to LED controller
        sn3218.enable_leds(self.led_status)
