# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
This module contains code to control the dome via an automationHAT.
"""
from ._astropy_init import *
import sys

# Enforce Python version check during package import.
# This is the same check as the one at the top of setup.py
__minimum_python_version__ = "3.6"


class UnsupportedPythonError(Exception):  # pragma: no cover
    pass


minimum = tuple((int(val) for val in __minimum_python_version__.split('.')))
if sys.version_info < minimum:  # pragma: no cover
    raise UnsupportedPythonError(
        f'domehunter does not support Python < {__minimum_python_version__}')

if not _ASTROPY_SETUP_:
    # For egg_info test builds to pass, put package imports here.
    pass
