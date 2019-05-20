"""Test eyetracker use.

Note: The Tobii Python API makes heavy use of global variables. This does not
work well across modules, because Python's "global" variables are in truth
module-bound variables. Apart from the "builtins", there are no "cross-module
variables."

Hence, we cannot define the functions that provide global variables in the
`define_eyetracker.py` module and import them here, because the imported
functions would *not* modify their global variables in the scope of this module
(the module doing the importing).

To resolve this, we define the functions using global variables in every
module that they need to be used in ... and in the eyetracking testing module
as well. This comes at the expense of identical code being defined in multiple
places and the resulting risk that these identical instances become somehow
changed and are no longer identical.

I'd be very happy to hear about a potential solution.

"""
import os
import pytest
from functools import partial
import csv

import numpy as np
import pandas as pd

from sp_experiment.define_eyetracker import find_eyetracker

########## global variable functions ####################
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
    global gaze
    gaze = (gaze_data['left_gaze_point_on_display_area'],
            gaze_data['right_gaze_point_on_display_area'])
########################


def test_find_eyetracker():
    """Test finding the eyetracker."""
    # We assume that when testing, the eyetracker will not be connected
    with pytest.raises(RuntimeError):
        find_eyetracker()


def test_get_gaze_data_callback():
    """Test the logging and making gaze_data globally available."""
    # make temp file with a hash so that it does probably not exist
    fname = 'tmp_ba0a6dd03443308b2ef5caa84ed30726fc2e368b.tsv'

    # Set an initial gaze

    # Make our callback function
    gaze_data_callback = get_gaze_data_callback(fname)

    # Pretend providing some gaze_data
    # this is usually provided from the eyetracker that is subscribed to
    gaze_data = {'left_gaze_point_on_display_area': 0.3,
                 'right_gaze_point_on_display_area': 0.7}
    gaze_data_callback(gaze_data)

    assert gaze[0] == 0.3
    assert gaze[1] == 0.7

    gaze_data = {'left_gaze_point_on_display_area': 0.4,
                 'right_gaze_point_on_display_area': 0.6}
    gaze_data_callback(gaze_data)

    assert gaze[0] == 0.4
    assert gaze[1] == 0.6

    # Check that logging worked as well
    df = pd.read_csv(fname, sep='\t')
    arr_left = df['left_gaze_point_on_display_area'].to_numpy()
    arr_right = df['right_gaze_point_on_display_area'].to_numpy()
    np.testing.assert_array_equal(arr_left, np.array((0.3, 0.4)))
    np.testing.assert_array_equal(arr_right, np.array((0.7, 0.6)))

    # clean up
    os.remove(fname)
