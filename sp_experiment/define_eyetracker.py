"""Functions and settings for the tobii 4C eye tracker.

Tobii Research "Pro" license is required (to be purchased separately).

Perform the calibration using the Tobii Pro Eyetracker Manager tool.
"""
import os
import csv
from functools import partial

import tobii_research as tr

# global gaze_dict allows us to share the gazepoint of the left and right eye
# as a tuple. By default it's set to be at (0, 0)
gaze_dict = {'gaze': (0, 0)}


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


def get_gaze_data_callback(fout_name):
    """Get a gaze_data_callback for the eyetracker.

    Parameters
    ----------
    fout_name : str
        Filename of the file in which to save gaze data.

    Returns
    -------
    gaze_data_callback : callable
        Function to be used in method call to an eyetracker object in the form
        `eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)`  # noqa: E501

    """
    gaze_data_callback = partial(_gaze_data_callback, fout_name=fout_name)
    return gaze_data_callback


def _gaze_data_callback(gaze_data, fout_name):
    """Get gaze_data from the eyetracker, make available, and save to file."""
    if not os.path.exists(fout_name):
        with open(fout_name, 'w') as f:
            w = csv.DictWriter(f, gaze_data.keys(), delimiter='\t')
            w.writeheader()
            w.writerow(gaze_data)
    else:
        with open(fout_name, 'a') as f:
            w = csv.DictWriter(f, gaze_data.keys(), delimiter='\t')
            w.writerow(gaze_data)

    # Make gazepoint available
    global gaze_dict
    gaze_dict['gaze'] = (gaze_data['left_gaze_point_on_display_area'],
                         gaze_data['right_gaze_point_on_display_area'])
