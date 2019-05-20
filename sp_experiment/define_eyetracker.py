"""Functions and settings for the tobii 4C eye tracker.

Tobii Research "Pro" license is required (to be purchased separately).

Perform the calibration using the Tobii Pro Eyetracker Manager tool.
"""
import os
import csv
from functools import partial

import tobii_research as tr


def find_eyetracker():
    """Find Tobii 4C eyetracker."""
    # Connect to the eyetracker
    found_eyetrackers = tr.find_all_eyetrackers()
    if len(found_eyetrackers) == 0:
        raise RuntimeError('No Eyetracker found. Did you connect it?')
    eyetracker = found_eyetrackers[0]
    print('\nEYETRACKER INFO\n')
    print('Address: ' + eyetracker.address)
    print('Model: ' + eyetracker.model)
    print('Name (It is OK if this is empty): ' + eyetracker.device_name)
    print('Serial number: ' + eyetracker.serial_number)
    print('Sampling freq: {}Hz'.format(eyetracker.get_gaze_output_frequency()))
    return eyetracker
