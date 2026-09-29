# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
This module contains code to control the dome via an automationHAT.
"""
import sys

__version__ = "0.1.dev0"

__minimum_python_version__ = "3.9"


class UnsupportedPythonError(Exception):
    pass


minimum = tuple((int(val) for val in __minimum_python_version__.split('.')))
if sys.version_info < minimum:
    raise UnsupportedPythonError(
        f'domehunter does not support Python < {__minimum_python_version__}')
