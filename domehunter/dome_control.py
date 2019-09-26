"""Run dome control on a raspberry pi GPIO."""


import sys
import time
import warnings

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
                 ENCODER_PIN_NUMBER=26,
                 HOME_SENSOR_PIN_NUMBER=20,
                 ROTATION_RELAY_PIN_NUMBER=13,
                 DIRECTION_RELAY_PIN_NUMBER=19,
                 BOUNCE_TIME=0.1,
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
        - A digital input device for the encoder (`ENCODER_PIN_NUMBER`)
        - A digital input device for the home sensor (`HOME_SENSOR_PIN_NUMBER`)
        - A digital output device for the motor on/off relay switch
          (`ROTATION_RELAY_PIN_NUMBER`)
        - A digital output device for the motor direction (CW/CCW) relay switch
          (`DIRECTION_RELAY_PIN_NUMBER`)

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
        ENCODER_PIN_NUMBER : int
            The GPIO pin that corresponds to the encoder input on the
            automationHAT (input 1).
        HOME_SENSOR_PIN_NUMBER : int
            The GPIO pin that corresponds to the home input on the
            automationHAT (input 2).
        ROTATION_RELAY_PIN_NUMBER : int
            The GPIO pin that corresponds to the rotation relay on the
            automationHAT (relay 1). The normally open terminal on the
            rotation relay is connected to the common terminal of the direction
            relay.
        DIRECTION_RELAY_PIN_NUMBER : int
            The GPIO pin that corresponds to the direction relay on the
            automationHAT (relay 2). The Normally Open (NO) relay position
            corresponds to clockwise (CW) and the Normally Closed (NC)
            position corresponds to counterclockwise (CCW).
        BOUNCE_TIME : float
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
            self.encoder_pin = Device.pin_factory.pin(ENCODER_PIN_NUMBER)
            self.home_sensor_pin = Device.pin_factory.pin(
                HOME_SENSOR_PIN_NUMBER)
        else:
            # set the timeout length variable to 5 minutes (units of seconds)
            WAIT_TIMEOUT = 5*60

        # set a wait time for testing mode that exceeds BOUNCE_TIME
        self.test_mode_delay_duration = BOUNCE_TIME + 0.05
        # set the timeout for wait_for_active()
        self.wait_timeout = WAIT_TIMEOUT

        # led_status is set with binary number, each zero/position sets the
        # state of an LED, where 0 is off and 1 is on
        self.led_status = 0b000000000000000000
        # create a dictionary of the LED name as the key and the digit of
        # the self.led_status binary integer it corresponds to. This means
        # we can convert the binary integer to a string and use the index
        # to change a 0 to 1 and vice versa and then convert back to a
        # binary integer. The updated self.led_status can then be sent to
        # the LED controller.
        self.led_lights_ind = {
            'power': 2,
            'comms': 3,
            'warn': 4,
            'input_1': 5,
            'input_2': 6,
            'input_3': 7,
            'relay_3_normally_closed': 8,
            'relay_3_normally_open': 9,
            'relay_2_normally_closed': 10,
            'relay_2_normally_open': 11,
            'relay_1_normally_closed': 12,
            'relay_1_normally_open': 13,
            'output_3': 14,
            'output_2': 15,
            'output_1': 16,
            'adc_3': 17,
            'adc_2': 18,
            'adc_1': 19
        }
        if debug_lights:  # pragma: no cover
            # if we are actually using the debug lights we can enable them now
            sn3218.output([0x10] * 18)
            sn3218.enable_leds(self.led_status)
            sn3218.enable()

        # initialize az as unknown, to ensure we have properly calibrated az
        self.testing = testing
        self.debug_lights = debug_lights
        # dome wont be moving when initlialised
        self._dome_moving = False
        self.dome_az = None
        # set the desired home_az
        self.home_az = home_azimuth

        # create a instance variable to track the dome motor encoder ticks
        self.encoder_count = 0
        # bounce_time settings gives the time in seconds that the device will
        # ignore additional activation signals
        self.encoder = DigitalInputDevice(
            ENCODER_PIN_NUMBER, bounce_time=BOUNCE_TIME)
        # _increment_count function to run when encoder is triggered
        self.encoder.when_activated = self._increment_count
        # set dummy value initially to force a rotation calibration run
        self.az_per_tick = None

        self._set_not_home()
        self.home_sensor = DigitalInputDevice(
            HOME_SENSOR_PIN_NUMBER, bounce_time=BOUNCE_TIME)
        # _set_not_home function is run when upon home senser deactivation
        self.home_sensor.when_deactivated = self._set_not_home
        # _set_at_home function is run when home sensor is activated
        self.home_sensor.when_activated = self._set_at_home

        # these two DODs control the relays that control the dome motor
        # the rotation relay is the on/off switch for dome rotation
        # the direction relay will toggle either the CW or CCW direction
        # (using both the normally open and normally close relay terminals)
        # so when moving the dome, first set the direction relay position
        # then activate the rotation relay
        self.rotation_relay = DigitalOutputDevice(
            ROTATION_RELAY_PIN_NUMBER, initial_value=False)
        self.direction_CW_relay = DigitalOutputDevice(
            DIRECTION_RELAY_PIN_NUMBER, initial_value=False)
        # because we initialiase the relay in the normally closed position
        self.current_direction = "CCW"

        # turn on the relay LEDs if we are debugging
        if debug_lights:  # pragma: no cover
            self._turn_led_on(leds=['relay_2_normally_closed'])
            self._turn_led_on(leds=['relay_1_normally_closed'])

###############################################################################
# Properties
###############################################################################

    @property
    def is_home(self):
        """Send True if the dome is at home."""
        return self._at_home

    @property
    def dome_in_motion(self):
        """Send True if dome is in motion.

        This property is set to false by the _stop_moving() private method
        and to set to true by the _move_cw() and _move_ccw() private methods.
        """
        return self._dome_moving

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
        if self.dome_az is None:
            print("Cannot return Azimuth as Dome is not yet calibrated.\
                   Run calibration loop")
        return self.dome_az

    def GotoAz(self, az):
        """
        Send Dome to a requested Azimuth position.

        Parameters
        ----------
        az : float
            Desired dome azimuth position in degrees.

        """
        if self.dome_az is None:
            print('Dome is not yet calibrated, running through calibration'
                  ' procedure, then will go to AZ specified.')
            self.calibrate_dome_encoder_counts()

        delta_az = int(az - self.dome_az)
        # determine whether CW or CCW gives the short path to desired az
        while abs(delta_az) > 180:
            if delta_az > 180:
                delta_az -= 360
            elif delta_az < -180:
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
                else:
                    # micro break to spare the little rpi cpu
                    time.sleep(0.1)
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
                else:
                    # micro break to spare the little rpi cpu
                    time.sleep(0.1)
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
        # now set dome to rotate num_cal_rotations times so we can determine
        # the number of ticks per revolution
        while rotation_count < num_cal_rotations:
            self._move_cw()
            if self.testing:
                # tell the fake home sensor that we have left home
                self.home_sensor_pin.drive_low()
                self._simulate_ticks(num_ticks=10)
            # need to introduce a small pause before wait_for_active as we
            # start from home position and want to make sure we clear the
            # sensor before we start waiting for it to come around again
            time.sleep(0.5)
            self.home_sensor.wait_for_active(timeout=self.wait_timeout)

            if self.testing:
                # tell the fake home sensor that we have come back to home
                time.sleep(0.1)
                self.home_sensor_pin.drive_high()

            self._stop_moving()
            # another short pause to get an obvious blink of debug_lights
            time.sleep(0.1)

            rotation_count += 1

        # set the azimuth per encoder tick factor based on how many ticks we
        # counted over n rotations
        self.az_per_tick = 360 / (self.encoder_count / rotation_count)
        # set dome azimuth to home_az position
        # problem: this isn't compensating for any overshooting
        self.dome_az = self.home_az

    def find_home(self):
        """
        Move Dome to home position.

        """
        # if dome already home, do nothing
        if self.is_home:
            self.encoder_count = 0
        else:
            self._move_cw()
            time.sleep(0.1)
            self.home_sensor.wait_for_active(timeout=self.wait_timeout)
            if self.testing:
                # in testing mode need to "fake" the activation of the home pin
                time.sleep(0.5)
                self.home_sensor_pin.drive_high()

            self._stop_moving()
            self.dome_az = self.home_az
            self.encoder_count = 0

###############################################################################
# Private Methods
###############################################################################

    def _set_at_home(self):
        """
        Update home status to at home and debug LEDs (if enabled).
        """
        self._turn_led_on(leds=['input_2'])
        self._at_home = True

    def _set_not_home(self):
        """
        Update home status to not at home and debug LEDs (if enabled).
        """
        self._turn_led_off(leds=['input_2'])
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
        self._turn_led_on(leds=['input_1'])
        time.sleep(0.01)
        self._turn_led_off(leds=['input_1'])

        if self.current_direction is None:
            self.current_direction = self.last_direction

        if self.current_direction == "CW":
            self.encoder_count += 1
        elif self.current_direction == "CCW":
            self.encoder_count -= 1
        # TODO what is last_direction is also None?

    def _az_to_ticks(self, az):
        """
        Convert degrees (azimuth) to equivalent in encoder tick count. Because
        we zero the encoder at the home position, this conversion needs to
        take into account the offset between the zero azimuth position and the
        zero encoder position.

        Parameters
        ----------
        az : int
            Dome azimuth position in degrees.

        Returns
        -------
        int
            Returns azimuth position to corresponding encoder tick count.

        """
        return int((az - self.home_az) % 360 / self.az_per_tick)

    def _ticks_to_az(self, ticks):
        """
        Convert encoder tick count to equivalent in degrees (azimuth).

        Parameters
        ----------
        ticks : integer
            The number of encoder ticks recorded.

        Returns
        -------
        float
            The corresponding dome azimuth position in degrees.

        """
        return ticks * self.az_per_tick

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
            self.home_sensor_pin.drive_low()
        # update the last_direction instance variable
        self.last_direction = self.current_direction
        # now update the current_direction variable to CW
        self.current_direction = "CW"
        # set the direction relay switch to CW position
        self.direction_CW_relay.on()
        # update the debug LEDs
        if self.last_direction == "CCW":
            self._turn_led_off(leds=['relay_2_normally_closed'])
        self._turn_led_on(leds=['relay_2_normally_open'])
        # turn on rotation
        self.rotation_relay.on()
        self._dome_moving = True
        # update the rotation relay debug LEDs
        self._turn_led_on(leds=['relay_1_normally_open'])
        self._turn_led_off(leds=['relay_1_normally_closed'])
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
            self.home_sensor_pin.drive_low()
        # update the last_direction instance variable
        self.last_direction = self.current_direction
        # now update the current_direction variable to CCW
        self.current_direction = "CCW"
        # set the direction relay switch to CCW position
        self.direction_CW_relay.off()
        self._dome_moving = False
        # update the debug LEDs
        if self.last_direction == "CW":
            self._turn_led_off(leds=['relay_2_normally_open'])
        self._turn_led_on(leds=['relay_2_normally_closed'])
        # turn on rotation
        self.rotation_relay.on()
        # update the rotation relay debug LEDs
        self._turn_led_on(leds=['relay_1_normally_open'])
        self._turn_led_off(leds=['relay_1_normally_closed'])
        cmd_status = True
        return cmd_status

    def _stop_moving(self):
        """
        Stop dome movement by switching the dome rotation relay off.
        """
        self.rotation_relay.off()
        self._dome_moving = False
        # update the debug LEDs
        self._turn_led_off(leds=['relay_1_normally_open'])
        self._turn_led_on(leds=['relay_1_normally_closed'])
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
            self.encoder_pin.drive_low()
            # test_mode_delay_duration is set so that it will always exceed
            # the set bounce_time
            # of the pins
            time.sleep(self.test_mode_delay_duration)
            self.encoder_pin.drive_high()
            time.sleep(self.test_mode_delay_duration)
            tick_count += 1

    def _turn_led_on(self, leds=[]):  # pragma: no cover
        """
        Method of turning a set of debugging LEDs on

        Parameters
        ----------
        leds : list
            List of LED name string to indicate which LEDs to turn on.

        """
        # pass a list of strings of the leds to turn on
        if not(self.debug_lights):
            return None
        if leds == []:
            # if leds is an empty list do nothing
            pass
        # this function needs a bunch of checks at some point
        # like length of the binary number, whether things have the right
        # type at the end (binary int vs string vs list) etc etc
        #
        # take the current led_status and convert to a string in binary
        # format (18bit)
        new_state = format(self.led_status, '#020b')
        # from that string create a list of characters
        # use the keys in the leds list and the led_lights_ind
        new_state = list(new_state)
        for led in leds:
            ind = self.led_lights_ind[led]
            new_state[ind] = '1'
        # convert the updated list to a string and then to a binary int
        new_state = ''.join(new_state)
        self.led_status = int(new_state, 2)
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
        # pass a list of strings of the leds to turn off
        if not(self.debug_lights):
            return None
        if leds == []:
            # if leds is an empty list do nothing
            pass
        # take the current led_status and convert to a string in binary
        # format (18bit)
        new_state = format(self.led_status, '#020b')
        # from that string create a list of characters
        # use the keys in the leds list and the led_lights_ind
        new_state = list(new_state)
        for led in leds:
            ind = self.led_lights_ind[led]
            new_state[ind] = '0'
        # convert the updated list to a string and then to a binary int
        new_state = ''.join(new_state)
        self.led_status = int(new_state, 2)
        # pass the new binary int to LED controller
        sn3218.enable_leds(self.led_status)
