"""Run dome control a raspberry pi GPIO."""


class DomePiSubsystem():
    """Abstract base class for pi GPIO subsystems."""

    def __init__(self, device_name, *args, **kwargs):
        """Initialize a Pi subsystem with no connection to underlying device.

        Maybe this will have common configuration info for the various
        GPIO subsystems?
        """

        self._device_name = device_name

    def stop(self):
        print(f"Stopping {self._device_name}")


class DomePi():
    """Interface to dome control raspberry pi GPIO.

    Might start with: https://gpiozero.readthedocs.io/en/stable/
    but might use something else if we buy a fancy Pi HAT.
    """

    def __init__(self, *args, **kwargs):
        """Setup raspberry pi GPIO."""

        self._rotator = DomePiSubsystem(device_name="rotator")
        self._home_sensor = DomePiSubsystem(device_name="home sensor")
        self._encoder = DomePiSubsystem(device_name="encoder")

        self._subsystems = [self._rotator, self._home_sensor, self._encoder]

    def move_ccw(self, degrees):
        print(f"Sending GPIO move_ccw({degrees}) command.")

    def all_stop(self):
        for subsystem in self._subsystems:
            subsystem.stop()
