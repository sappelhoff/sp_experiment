"""Test eyetracker use."""
import os
import pytest

import numpy as np
import pandas as pd

from sp_experiment.define_eyetracker import (find_eyetracker,
                                             get_gaze_data_callback,
                                             gaze_dict)


def test_find_eyetracker():
    """Test finding the eyetracker."""
    # We assume that when testing, the eyetracker will not be connected
    with pytest.raises(RuntimeError):
        find_eyetracker()


def test_get_gaze_data_callback():
    """Test the logging and making gaze_data globally available."""
    # make temp file with a hash so that it does probably not exist
    fname = 'tmp_ba0a6dd03443308b2ef5caa84ed30726fc2e368b.tsv'

    # Check the initial gaze
    assert gaze_dict['gaze'][0] == 0
    assert gaze_dict['gaze'][1] == 0

    # Make our callback function
    gaze_data_callback = get_gaze_data_callback(fname)

    # Pretend providing some gaze_data
    # this is usually provided from the eyetracker that is subscribed to
    gaze_data = {'left_gaze_point_on_display_area': 0.3,
                 'right_gaze_point_on_display_area': 0.7}
    gaze_data_callback(gaze_data)

    # It should have updated our global gaze_dict
    assert gaze_dict['gaze'][0] == 0.3
    assert gaze_dict['gaze'][1] == 0.7

    # Try to update again
    gaze_data = {'left_gaze_point_on_display_area': 0.4,
                 'right_gaze_point_on_display_area': 0.6}
    gaze_data_callback(gaze_data)

    assert gaze_dict['gaze'][0] == 0.4
    assert gaze_dict['gaze'][1] == 0.6

    # Check that logging to a file worked as well
    df = pd.read_csv(fname, sep='\t')
    arr_left = df['left_gaze_point_on_display_area'].to_numpy()
    arr_right = df['right_gaze_point_on_display_area'].to_numpy()
    np.testing.assert_array_equal(arr_left, np.array((0.3, 0.4)))
    np.testing.assert_array_equal(arr_right, np.array((0.7, 0.6)))

    # clean up
    os.remove(fname)
