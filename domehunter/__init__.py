# Licensed under a 3-clause BSD style license - see LICENSE.rst

# Packages may add whatever they like to this file, but
# should keep this content at the top.
# ----------------------------------------------------------------------------
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

from .x2dome import X2Dome
from .domepi import DomePi


def create_dome():
    """Create a X2 bridge to a raspberry Pi Dome controller.

    Maybe this will just setup the configuration via a yaml.
    """
    dome = HuntsmanDome()
    print("Dome created.")
    return(dome)


class HuntsmanDome():
    """Class that establishes link between TSX and the Pi via X2.
    """

    def __init__(self, *args, **kwargs):
        """Initalize the Pi GPIO and establish X2 port."""
        self._x2driver = X2Dome()
        self._domepi = DomePi()
        self._west_is_ccw = True

    def move_ccw(self, degrees_ccw):
        print(f"Sending command to move {degrees_ccw} CCW")
        cmd_status = self._domepi.move_ccw(degrees_ccw)
        return cmd_status

    def move_west(self, degrees_west):
        print(f"Sending command to move {degrees_west} West")
        if self._west_is_ccw:
            cmd_status = self._domepi.move_ccw(degrees_west)
        else:
            cmd_status = self._domepi.move_cw(degrees_west)

        return cmd_status

    def start_daemon(self):
        print("Starting dome control daemon.")
        x2driver = self._x2driver.connect()
        return x2driver

    def halt_daemon(self):
        print("Halting dome control daemon")
        self._x2driver.disconnect()
        self._domepi.all_stop()
