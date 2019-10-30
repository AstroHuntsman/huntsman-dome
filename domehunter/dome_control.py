"""Run dome control on a raspberry pi GPIO."""


import math
import sys
import os
import threading
import time
import warnings
import logbook
from logbook import TimedRotatingFileHandler as TRFH
from logbook import StderrHandler as StdH
import yaml
from contextlib import suppress

import astropy.units as u
from astropy.coordinates import Angle, Longitude
from gpiozero import Device, DigitalInputDevice, DigitalOutputDevice
from gpiozero.pins.mock import MockFactory

from domehunter.enumerations import Direction, LED_Lights, ReturnCode

from ._astropy_init import *

logger = logbook.Logger(__name__)
fmt_str = ('[{record.time:%Y-%m-%d %H:%M:%S}]'
           ' line {record.lineno:<3} in '
           '{record.module:<}.{record.func_name:<} of {record.filename}\n    '
           '[{record.level_name:*^11}] : {record.message:<20}')

logfilename = os.path.join(os.path.dirname(__file__), 'logs/domepi.log')
logger.handlers.append(TRFH(logfilename,
                            level='NOTICE',
                            mode='a+',
                            date_format='%Y-%m-%d',
                            bubble=True,
                            format_string=fmt_str))

logger.handlers.append(StdH(level='NOTICE',
                            bubble=True,
                            format_string=fmt_str))

# if we want to use the automation hat status lights we need to
# import the pimoroni led driver
try:  # pragma: no cover
    import sn3218
    sn3218.disable()
except OSError:  # pragma: no cover
    wmsg = ("AutomationHAT hardware not detected, "
            "testing=True and debug_lights=False recommended.")
    logger.warning(
        ("AutomationHAT hardware not detected, "
         "testing=True and debug_lights=False recommended.")
        )
except Exception:  # pragma: no cover
    wmsg = ("Something went wrong in importing sn3218, "
            "status lights unlikely to work.")
    logger.warning(
        ("Something went wrong in importing sn3218, "
         "status lights unlikely to work.")
        )

# ----------------------------------------------------------------------------


# TODO: set up functions to raise custom exceptions to allow server to
#       properly handle exceptions
class DomeCommandError(Exception):  # pragma: no cover
    # generic dome command error, placeholder for now
    pass


def load_dome_config(config_path=None):
    """Load dome configuration infomation from a yaml file.

    Parameters
    ----------
    config_path : str
        File path of desired configuration yaml file.

    Returns
    -------
    type dict
        Dictionary of keyword args to pass through to dome instance.

    """
    if config_path is None:
        directory = os.path.abspath(os.path.dirname(__file__))
        rel_path = 'gRPC-server/dome_controller_config.yml'
        config_path = os.path.join(directory, rel_path)
    try:
        with open(config_path, 'r') as f:
            config = yaml.load(f.read(), Loader=yaml.FullLoader)
    except Exception as e:
        logger.warning(f'Error loading yaml config, {e}')
    return config


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
                 home_azimuth,
                 testing=True,
                 debug_lights=False,
                 log_file_level='notice',
                 log_stderr_level='notice',
                 az_position_tolerance=1.0,
                 degrees_per_tick=None,
                 encoder_pin_number=26,
                 home_sensor_pin_number=20,
                 rotation_relay_pin_number=13,
                 direction_relay_pin_number=19,
                 bounce_time=0.001,
                 led_brightness=0x10,
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
        home_azimuth: float
            The home azimuth position in degrees (integer between 0 and 360).
        testing : boolean
            Toggle to enable a simulated hardware testing mode.
        debug_lights : boolean
            Toggle to enable the status LEDs on the automationHAT.
        log_level : str
            The log level to set after initialisation is complete.
        az_position_tolerance: float
            The tolerance, in units of degrees, used during goto_az() calls.
            Dome will move to requested position to within this tolerance. If
            the calibrated degrees_per_tick is greater than
            az_position_tolerance, degrees_per_tick will be used as the
            tolerance instead.
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
        logger.notice(f'Dome testing: {testing} lights: {debug_lights}')

        if testing:
            logger.info(f'Creating Dome in testing mode')
            # Set the default pin factory to a mock factory
            Device.pin_factory = MockFactory()
            # in case a previous instance has been initialised, tell the
            # pin factory to release all the pins
            Device.pin_factory.reset()
            # set a timeout length in seconds for wait_for_active() calls
            WAIT_TIMEOUT = 2*60

            # in testing mode we need to create a seperate pin object so we can
            # simulate the activation of our fake DIDs and DODs
            self._encoder_pin = Device.pin_factory.pin(encoder_pin_number)
            self._home_sensor_pin = Device.pin_factory.pin(
                home_sensor_pin_number)
        else:
            # set the timeout length variable to 5 minutes (units of seconds)
            WAIT_TIMEOUT = 10 * 60

        # set a wait time for testing mode that exceeds bounce_time
        self.test_mode_delay_duration = bounce_time + 0.05
        # set the timeout for wait_for_active()
        self.wait_timeout = WAIT_TIMEOUT
        logger.info(f'wait_timeout: {self.wait_timeout}')

        self.testing = testing
        self.debug_lights = debug_lights

        # TODO: read in default value from yaml(?)
        if degrees_per_tick is None:
            logger.warning(
                (f'No value supplied for degrees_per_tick, '
                 f'dome requires calibration.')
                )
            self._degrees_per_tick = degrees_per_tick
        else:
            self._degrees_per_tick = Angle(degrees_per_tick * u.deg)
        self._az_position_tolerance = Angle(az_position_tolerance * u.deg)
        self.home_az = Longitude(home_azimuth * u.deg)
        # need something to let us know when dome is calibrating so home sensor
        # activation doesnt zero encoder counts
        self._calibrating = False

        # NOTE: this led setup needs to be done before setting any callback
        # functions
        # turn on the relay LEDs if we are debugging
        # led_status is set with binary number, each zero/position sets the
        # state of an LED, where 0 is off and 1 is on
        self.led_status = LED_Lights.RELAY_1_NC | LED_Lights.RELAY_2_NC
        # the initial led_status is set to indicate the positions the relays
        # are initialised in (normally closed)
        # use the LED_Lights enum.Flag class to pass binary integers masks to
        # the _change_led_state() method.
        if debug_lights:  # pragma: no cover
            # Make sure LED brightness is turned up
            logger.info(f'Adjusting brightness for leds.')
            sn3218.output([led_brightness] * 18)
            # if we are actually using the debug lights we can enable them now
            logger.info(f'Setting relay LEDs to reflect initialised state.')
            self._change_led_state(1,
                                   leds=[LED_Lights.RELAY_1_NC,
                                         LED_Lights.RELAY_2_NC])
            sn3218.enable_leds(self.led_status.value)
            sn3218.enable()

        # create a instance variable to track the dome motor encoder ticks
        self._encoder_count = 0
        # upon initialising, dome is unhomed so dome az is unknown
        self._unhomed = True
        self._dome_az = None
        # create a threading abort event, to use for aborting movement commands
        self._abort_event = threading.Event()
        # creating a threading move event, to indicate when a move thread
        # is active
        self._move_event = threading.Event()
        # creating a threading simulated_rotation event, to indicate when a
        # simulated rotation thread is running for testing mode calibration
        self._simulated_rotation_event = threading.Event()
        # bounce_time settings gives the time in seconds that the device will
        # ignore additional activation signals
        logger.info(f'Connecting encoder on pin {encoder_pin_number}.')
        self._encoder = DigitalInputDevice(
            encoder_pin_number, bounce_time=bounce_time)
        # _increment_count function to run when encoder is triggered
        self._encoder.when_activated = self._increment_count
        self._encoder.when_deactivated = self._turn_off_input_1_led

        # these two DODs control the relays that control the dome motor
        # the rotation relay is the on/off switch for dome rotation
        # the direction relay will toggle either the CW or CCW direction
        # (using both the normally open and normally close relay terminals)
        # so when moving the dome, first set the direction relay position
        # then activate the rotation relay
        logger.info((f'Connecting rotation relay on '
                     f'pin {rotation_relay_pin_number}.'))
        self._rotation_relay = DigitalOutputDevice(
            rotation_relay_pin_number, initial_value=False)
        logger.info((f'Connecting direction relay on '
                    f'pin {direction_relay_pin_number}.'))
        self._direction_relay = DigitalOutputDevice(
            direction_relay_pin_number, initial_value=False)
        # because we initialiase the relay in the normally closed position
        logger.info(f'Setting start direction to CCW.')
        self.current_direction = Direction.CCW
        # need to set something for last direction now
        self.last_direction = Direction.NONE

        # Home Sensor
        logger.info(f'Connecting home sensor on pin {home_sensor_pin_number}.')
        self._home_sensor = DigitalInputDevice(
            home_sensor_pin_number, bounce_time=bounce_time)
        # _set_not_home function is run when upon home senser deactivation
        self._home_sensor.when_deactivated = self._set_not_home
        # _set_at_home function is run when home sensor is activated
        self._home_sensor.when_activated = self._set_at_home
        if self._home_sensor.is_active:
            self._set_at_home()
        else:
            self._set_not_home()

        # After initialising we may want to change the log level
        self.logger = logger
        self._update_handler_level('TRFH', log_file_level)
        self._update_handler_level('StdH', log_stderr_level)

    def __del__(self):
        """
        Class deconstructer, attempts to turn off all LEDs, terminate
        any active movements and release gpio pins.
        """
        with suppress(Exception):
            self.abort()
        with suppress(Exception):
            self._rotation_relay.off()
        with suppress(Exception):
            if self.debug_lights:
                self._change_led_state(0, [led for led in LED_Lights])
        with suppress(Exception):
            Device.pin_factory.reset()

###############################################################################
# Properties
###############################################################################

    @property
    def dome_az(self):
        """Returns the dome azimuth in degrees."""
        self._dome_az = self._ticks_to_az(self.encoder_count)
        if self._dome_az is None or self._unhomed:
            print("Dome az unknown, please home the dome.")
        logger.debug(f'Dome azimuth: {self._dome_az}.')
        return self._dome_az

    @property
    def at_home(self):
        """Return True if the dome is at home."""
        home_active = self._home_sensor.is_active
        logger.debug(f'Home active: {home_active}.')
        return home_active

    @property
    def dome_in_motion(self):
        """Send True if dome is in motion."""
        dome_motion = self._rotation_relay.is_active
        logger.debug(f'Dome in motion: {dome_motion}.')
        return dome_motion

    @property
    def movement_thread_active(self):
        """Return true if a movement thread is running"""
        return self._move_event.is_set()

    @property
    def encoder_count(self):
        """Returns the current encoder count."""
        logger.debug(f'Encoder count: {self._encoder_count}.')
        return self._encoder_count

    @property
    def degrees_per_tick(self):
        """Returns the calibrated azimuth (in degrees) per encoder tick."""
        logger.debug(f'Degrees per tick: {self._degrees_per_tick}.')
        return self._degrees_per_tick

    @property
    def az_position_tolerance(self):
        """
        Returns the azimuth position tolerance (in degrees).

        If the tolerance set at initialisation is less than degrees_per_tick
        use 1.5 * degrees_per_tick as the tolerance.
        """
        if self._az_position_tolerance < 1.5 * self.degrees_per_tick:
            logger.warning(
                (f'az_position_tolerance [{self._az_position_tolerance}] is '
                 f'less than 1.5 times degrees_per_tick. Setting tolerance '
                 f'to 1.5 * degrees_per_tick')
                )
        tolerance = max(self._az_position_tolerance,
                        1.5 * self.degrees_per_tick)
        self._az_position_tolerance = tolerance
        return tolerance

    @property
    def log_levels(self):
        """
        Returns the current log level of the logger for this module.
        """
        filelvl = self._get_handler('TRFH').level_name
        stderrlvl = self._get_handler('StdH').level_name
        self.logger.notice((f'Log file handler level is: {filelvl}, '
                            f'Stderr handler level is: {stderrlvl}'))
        return

###############################################################################
# Methods
###############################################################################

    """These correspond to the AbstractMethods created by RPC."""

    def abort(self):
        """
        Stop everything by switching the dome motor on/off relay to off.

        """
        # TODO: consider another way to do this in case the relay fails/sticks
        # one way might be cut power to the automationHAT so the motor relays
        # will receive no voltage even if the relay is in the open position?
        logger.warning(f'Aborting dome movement.')
        # set the abort event thread flag
        self._abort_event.set()
        # wait for threads to abort
        while self.movement_thread_active:
            time.sleep(0.1)
        self._abort_event.clear()

    def goto_az(self, az):
        """
        Send Dome to a requested Azimuth position.

        Parameters
        ----------
        az : float
            Desired dome azimuth position in degrees.

        """
        if self.dome_az is None:
            return
        if self.movement_thread_active:
            logger.warning('Movement command in progress.')
            return

        target_az = Longitude(az * u.deg)
        logger.notice(f'Go to target azimuth [{target_az}].')

        # calculate delta_az, wrapping at 180 to ensure we take shortest route
        delta_az = (target_az - self.dome_az).wrap_at(180 * u.degree)
        logger.info(f'Delta azimuth [{delta_az}].')

        self._move_event.set()
        if delta_az > 0:
            self._rotate_dome(Direction.CW)
        else:
            self._rotate_dome(Direction.CCW)
        # wait until encoder count matches desired delta az
        goingto_az = threading.Thread(target=self._thread_condition,
                                      args=(self._goto_az_complete,
                                            target_az))
        goingto_az.start()

    def calibrate_dome_encoder_counts(self, num_cal_rotations=2):
        """
        Calibrate the encoder (determine degrees per tick).

        Parameters
        ----------
        num_cal_rotations : integer
            Number of rotations to perform to calibrate encoder.

        """
        if self.movement_thread_active:
            logger.warning('Movement command in progress.')
            return
        # rotate the dome until we hit home, to give reference point
        logger.notice(f'Finding Home.')
        self.find_home()
        while self.movement_thread_active:
            # wait for find_home() to finish
            time.sleep(0.1)
        logger.notice(f'Found Home.')
        # pause to let things settle/get a noticeable blink of debug_lights
        time.sleep(0.5)

        # instance variable to track rotations during calibration
        self._rotation_count = 0
        # instance variable that is over written in calibrate routine
        self._num_cal_rotations = num_cal_rotations
        # now set dome to rotate num_cal_rotations times so we can determine
        # the number of ticks per revolution
        logger.notice(
            (f'Starting calibration rotations.')
            )
        self._move_event.set()
        self._rotate_dome(Direction.CW)
        self._calibrating = True

        cal_monitor = threading.Thread(target=self._thread_condition,
                                       args=(self._calibration_complete,))
        if self.testing:
            calibrate_sim = threading.Thread(target=self._simulate_calibration)
            calibrate_sim.start()
        cal_monitor.start()

    def find_home(self):
        """
        Move Dome to home position.

        """
        if self.movement_thread_active:
            logger.warning('Movement command in progress.')
            return
        # iniate the movement and set the _move_event flag
        logger.notice(f'Finding Home.')
        self._unhomed = True
        self._move_event.set()
        self._rotate_dome(Direction.CW)
        time.sleep(0.1)
        homing = threading.Thread(target=self._thread_condition,
                                  args=(self._find_home_complete,))
        homing.start()
        if self.testing:
            # in testing mode need to "fake" the activation of the home pin
            home_pin_high = threading.Timer(0.5,
                                            self._home_sensor_pin.drive_high)
            home_pin_high.start()

    def sync(self, az):
        """
        Sync encoder count to azimuth position.

        Parameters
        ----------
        az : float
            Current dome azimuth position in degrees.

        """
        logger.notice(f'sync: syncing encoder counts to azimuth [{az}]')
        self._encoder_count = self._az_to_ticks(Longitude(az * u.deg))
        return

###############################################################################
# Private Methods
###############################################################################

    def _thread_condition(self, trigger_condition, *args, **kwargs):
        """Condition monitoring thread for movement commands.

        Will return when:
            - trigger_condition is true
            - abort event is triggered
            - thread running time exceeds self.wait_timeout

        Parameters
        ----------
        trigger_condition : callable method
            Callable method that returns a boolean value.

        """
        calibration_success = False
        # This will update to false, if while loop is terminated by
        # trigger_condition()
        # TODO: better system for flagging success/abort/timeout
        goingtoaz = False
        if trigger_condition.__name__ == '_goto_az_complete':
            goingtoaz = True
        start = time.monotonic()

        while True:
            wait_time = time.monotonic() - start
            if trigger_condition(*args, **kwargs):
                logger.info(
                    (f'Monitoring thread triggered '
                     f'by {trigger_condition.__name__}.')
                    )
                calibration_success = True
                break
            elif self._abort_event.is_set():
                logger.info(f'Monitoring thread triggered by abort event.')
                break
            elif wait_time > self.wait_timeout:
                logger.info(
                    (f'Monitoring thread triggered '
                     f'by timeout [{self.wait_timeout}s].')
                    )
                break
            elif goingtoaz and self.testing is True:
                # if testing simulate a tick for every cycle of while loop
                self._simulate_ticks(num_ticks=1)
            time.sleep(0.1)

        logger.info('Stopping dome movement.')
        self._stop_moving()

        if trigger_condition.__name__ == '_calibration_complete':
            # set the azimuth per encoder tick factor based on
            # how many ticks we counted over n rotations
            self._degrees_per_tick = Angle(
                360 / (self.encoder_count / self._rotation_count) * u.deg)
        # reset various dome state variables/events
        self._move_event.clear()
        self._calibrating = False
        return

    def _goto_az_complete(self, target_az):
        """Determines if current azimuth is within tolerance of target azimuth.

        Returns
        -------
        bool
            Returns true if self.dome_az is within tolerance of target azimuth.

        """
        raw_delta_az = (target_az - self.dome_az).wrap_at('180d')
        delta_az = self.current_direction * raw_delta_az
        logger.debug(
            (f'Delta_az is {delta_az}, '
             f'tolerance window is {self.az_position_tolerance}.')
            )
        return delta_az <= self.az_position_tolerance

    def _find_home_complete(self):
        """Return True if the dome is at home."""
        return self._home_sensor.is_active

    def _calibration_complete(self):
        """Return True if desired number of calibration rotations completed."""
        logger.debug(
            (f'Rotation count is [{self._rotation_count}], rotations '
             f'to go [{self._num_cal_rotations - self._rotation_count}].')
            )
        return self._rotation_count >= self._num_cal_rotations

    def _simulate_calibration(self):
        """Calibration method to be called from within a non-blocking thread"""
        start = time.monotonic()
        first_rotation = threading.Thread(target=self._simulate_rotation)
        first_rotation.start()

        while True:
            logger.debug(
                (f'Loop runtime is {time.monotonic() - start}: '
                 f'rot_count [{self._rotation_count}], '
                 f'encoder_count [{self.encoder_count}]')
                )
            if not self._simulated_rotation_event.is_set():
                time.sleep(1)
                logger.debug(
                    (f'Completion of simulated rotation detected, '
                     f'simulating next rotation.')
                    )
                sim_rotation = threading.Thread(target=self._simulate_rotation)
                if self._calibration_complete():
                    logger.debug(
                        (f'Calibration rotations completed, '
                         f'ending calibration.')
                        )
                    break
                sim_rotation.start()
            time.sleep(1)

    def _set_at_home(self):
        """
        Update home status to at home and debug LEDs (if enabled).
        """
        logger.notice('Home sensor activated.')
        self._change_led_state(1, leds=[LED_Lights.INPUT_2])
        self._unhomed = False
        # don't want to zero encoder while calibrating
        # note: because Direction.CW is +1 and Direction.CCW is -1, need to
        # add 1 to self.current_direction, to get CCW to evaluate to False
        if not self._calibrating and bool(self.current_direction + 1):
            logger.debug(
                (f'Passing home clockwise, zeroing encoder counts.')
                )
            self._encoder_count = 0
            logger.debug(
                (f'Encoder: {self.encoder_count} Azimuth: {self.dome_az}')
                )
        # if we are calibrating, increment the rotation count
        if self._calibrating:
            logger.debug(
                (f'Home triggered during calibration, '
                 f'incrementing calibration rotation count.')
                )
            self._rotation_count += 1

    def _set_not_home(self):
        """
        Update home status to not at home and debug LEDs (if enabled).
        """
        logger.notice(f'Home sensor deactivated.')
        self._change_led_state(0, leds=[LED_Lights.INPUT_2])

    def _increment_count(self):
        """
        Private method used for callback function of the encoder DOD.

        Calling this method will toggle the encoder debug LED (if enabled)
        and increment or decrement the encoder_count instance variable,
        depending on the current rotation direction of the dome.

        If the current dome direction cannot be determined, the last recorded
        direction is adopted.
        """
        logger.info(f"Encoder activated _increment_count.")
        self._change_led_state(1, leds=[LED_Lights.INPUT_1])

        logger.debug(
            (f'Direction: Current {self.current_direction} '
             f'Last {self.last_direction}.')
            )
        logger.debug(f'Encoder count before: {self.encoder_count}.')
        if self.current_direction != Direction.NONE:
            self._encoder_count += self.current_direction
        elif self.last_direction != Direction.NONE:
            self._encoder_count += self.last_direction
        else:
            raise RuntimeError(
                ("No current or last direction, can't increment count.")
                )

        # Set new dome azimuth
        # if dome is unhomed, _dome_az should remain as None
        if self._unhomed:
            logger.warning(f'Dome is unhomed, please home dome.')
        else:
            logger.debug(
                (f'Encoder: {self.encoder_count} Azimuth: {self.dome_az}.')
                )

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
        logger.debug(f'Home azimuth: {self.home_az} Convert Azimuth: {az}')
        az_rel_to_home = (az - self.home_az).wrap_at(360 * u.degree)
        logger.debug(f'Azimuth relative to home: {az_rel_to_home}')
        encoder_ticks = az_rel_to_home.degree / self.degrees_per_tick.degree
        logger.debug(f'Encoder ticks for requested az: {encoder_ticks}')
        return encoder_ticks

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
        logger.debug(f'Home azimuth: {self.home_az} Convert ticks: {ticks}')
        tick_to_deg = Longitude(ticks * self.degrees_per_tick)
        logger.debug(f'Ticks to degrees: {tick_to_deg}')
        az = Longitude(self.home_az + tick_to_deg)
        logger.debug(f'Azimuth for requested ticks: {az}')
        return az

    def _rotate_dome(self, direction):
        """
        Set dome to move clockwise.

        Returns
        -------
        integer
            Command status return code (tbd).

        """
        logger.info(f'Rotate dome direction: {direction}')
        # if testing, deactivate the home_sensor_pin to simulate leaving home
        if self.testing and self.at_home:
            self._home_sensor_pin.drive_low()
        # update the last_direction instance variable
        self.last_direction = self.current_direction
        logger.debug(f'Last direction set to {self.last_direction}.')
        # now update the current_direction variable to CW
        self.current_direction = direction
        # set the direction relay switch to CW position
        if self.current_direction == Direction.CW:
            logger.debug(f'Turning direction relay on (CW)')
            self._direction_relay.on()
            self._change_led_state(1, leds=[LED_Lights.RELAY_2_NO])
            self._change_led_state(0, leds=[LED_Lights.RELAY_2_NC])
        elif self.current_direction == Direction.CCW:
            logger.debug(f'Turning direction relay off (CCW).')
            self._direction_relay.off()
            self._change_led_state(0, leds=[LED_Lights.RELAY_2_NO])
            self._change_led_state(1, leds=[LED_Lights.RELAY_2_NC])
        # turn on rotation
        logger.debug(f'Turning on rotation relay.')
        self._rotation_relay.on()
        # update the rotation relay debug LEDs
        self._change_led_state(1, leds=[LED_Lights.RELAY_1_NO])
        self._change_led_state(0, leds=[LED_Lights.RELAY_1_NC])

    def _stop_moving(self):
        """
        Stop dome movement by switching the dome rotation relay off.
        """
        logger.debug(f'Turning off rotation relay.')
        self._rotation_relay.off()
        self._move_event.clear()
        # update the debug LEDs
        self._change_led_state(0, leds=[LED_Lights.RELAY_1_NO])
        self._change_led_state(1, leds=[LED_Lights.RELAY_1_NC])
        # update last_direction with current_direction at time of method call
        logger.debug(f'Setting last direction to {self.current_direction}.')
        self.last_direction = self.current_direction
        logger.debug(f'Setting current direction to none.')
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

    def _simulate_rotation(self, ticks_per_rotation=10):
        """
        Method to simulate a complete dome rotation while in testing mode.
        """
        self._simulated_rotation_event.set()
        self._home_sensor_pin.drive_low()
        self._simulate_ticks(ticks_per_rotation)
        self._home_sensor_pin.drive_high()
        self._simulated_rotation_event.clear()

    def _change_led_state(self, desired_state, leds=[]):  # pragma: no cover
        """
        Method of turning a set of debugging LEDs on

        Parameters
        ----------
        desired_state : bool
            Parameter to indicate whether leds are being turned on (1 or True)
            or if they are being turned off (0 or False).
        leds : list
            List of LED_Lights enums to indicate which LEDs to turn on.

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
        sn3218.enable_leds(self.led_status.value)

    def _turn_off_input_1_led(self):
        """
        Call back function for encoder pin, turns the status led off when
        encoder pin is deactivated.
        """
        self._change_led_state(0, leds=[LED_Lights.INPUT_1])

    def _get_log_level(self, level):
        """Returns the logbook log level corresponding to the supplied string.

        Parameters
        ----------
        level : str
            The name of the desired logging level.

        Returns
        -------
        new_level : int
            An integer corresponding to the requested log level.

        """
        levels = logbook.base._reverse_level_names
        try:
            new_level = levels[level]
        except KeyError:
            logger.error((f'Requested level [\'{level}\'] is not valid.'
                          f' Valid levels are {list(levels.keys())}.'))
            return
        return new_level

    def _get_handler(self, handler):
        """Returns a specific handler from the logger so that log level can
        be adjusted if required.

        Parameters
        ----------
        handler : str
            The desired handler from the logger.

        Returns
        -------
        handler : logbook.handler object
            The requested handler.

        """
        handlers = {'TRFH': TRFH,
                    'StdH': StdH}
        try:
            requested_handler = handlers[handler]
        except KeyError:
            logger.error((f'Desired Handler [\'{requested_handler}\'] is not'
                          f' a valid handler type.'
                          f' Valid types are {list(levels.keys())}.'))
            return
        for handler in self.logger.handlers:
            if isinstance(handler, requested_handler):
                return handler

    def _update_handler_level(self, handler, level):
        """Updates a handlers logging level.

        Parameters
        ----------
        handler_type : str
            The name of the handler you want to update.
        level : str
            The name of the desired logging level.

        """
        new_level = self._get_log_level(level)
        handler_to_update = self._get_handler(handler)
        if new_level or handler_to_update is None:
            logger.debug(f'Failed to update logger handler log level')
            pass
        handler_to_update.level = new_level
