#!/usr/bin/env python3

"""Example of how to move the dome CCW."""
from domehunter.dome_control import Dome
from astropy import units as u


def main(degrees_ccw,
         **kwargs):
    """Example of moving the dome CCW.

    See argparse help string below for details about parameters.
    """
    dome = Dome()
    dome_moved = dome._move_ccw(degrees_ccw)
    return dome_moved


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description="Example dome move to the CCW")
    parser.add_argument('--degrees_ccw', default=10,
                        help='Number of degrees CCW to move.')
    parser.add_argument('--verbose', action='store_true', default=False, help='Verbose.')

    args = parser.parse_args()
    args.degrees_ccw = float(args.degrees_ccw) * u.degree

    success = main(**vars(args))
    if args.verbose:
        if success:
            print(f"Dome successfully moved {args.degrees_ccw}")
        else:
            print("Error: Dome did not move")
