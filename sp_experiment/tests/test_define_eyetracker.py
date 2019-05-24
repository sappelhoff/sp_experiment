"""Test eyetracker use."""
import os
import pytest
import ast

import numpy as np
import pandas as pd

import sp_experiment
from sp_experiment.define_eyetracker import (find_eyetracker,
                                             get_gaze_data_callback,
                                             gaze_dict,
                                             get_normed_gazepoint)


def test_find_eyetracker():
    """Test finding the eyetracker."""
    # We assume that when testing, the eyetracker will not be connected
    with pytest.raises(RuntimeError):
        find_eyetracker()


def test_get_normed_gazepoint():
    """Test gazepoint conversion."""
    # Tobii has a system with (0, 0) in upper left
    # First take "default" gaze_dict
    gaze_dict = sp_experiment.define_eyetracker.gaze_dict
    gazepoint = get_normed_gazepoint(gaze_dict)
    np.testing.assert_array_equal(gazepoint, np.array((0, 0)))

    # Now try other "gazes"
    gaze_dict = {'gaze': ((0, 0), (0, 0))}
    gazepoint = get_normed_gazepoint(gaze_dict)
    np.testing.assert_array_equal(gazepoint, np.array((-1, 1)))

    gaze_dict = {'gaze': ((0, 1), (0, 1))}
    gazepoint = get_normed_gazepoint(gaze_dict)
    np.testing.assert_array_equal(gazepoint, np.array((-1, -1)))

    gaze_dict = {'gaze': ((1, 1), (1, 1))}
    gazepoint = get_normed_gazepoint(gaze_dict)
    np.testing.assert_array_equal(gazepoint, np.array((1, -1)))

    gaze_dict = {'gaze': ((1, 0), (1, 0))}
    gazepoint = get_normed_gazepoint(gaze_dict)
    np.testing.assert_array_equal(gazepoint, np.array((1, 1)))


def test_get_gaze_data_callback():
    """Test the logging and making gaze_data globally available."""
    # make temp file with a hash so that it does probably not exist
    fname = 'tmp_ba0a6dd03443308b2ef5caa84ed30726fc2e368b.tsv'

    # Check the initial gaze
    assert gaze_dict['gaze'][0][0] == 0.5
    assert gaze_dict['gaze'][0][1] == 0.5
    assert gaze_dict['gaze'][1][0] == 0.5
    assert gaze_dict['gaze'][1][1] == 0.5

    # Make our callback function
    gaze_data_callback = get_gaze_data_callback(fname)

    # Pretend providing some gaze_data
    # this is usually provided from the eyetracker that is subscribed to
    gaze_data = {'left_gaze_point_on_display_area': (0.3, 0),
                 'right_gaze_point_on_display_area': (0.7, 0)}
    gaze_data_callback(gaze_data)

    # It should have updated our global gaze_dict
    assert gaze_dict['gaze'][0][0] == 0.3
    assert gaze_dict['gaze'][1][0] == 0.7
    assert gaze_dict['gaze'][0][1] == 0
    assert gaze_dict['gaze'][1][1] == 0

    # Try to update again
    gaze_data = {'left_gaze_point_on_display_area': (0, 0.4),
                 'right_gaze_point_on_display_area': (0, 0.6)}
    gaze_data_callback(gaze_data)

    assert gaze_dict['gaze'][0][0] == 0
    assert gaze_dict['gaze'][1][0] == 0
    assert gaze_dict['gaze'][0][1] == 0.4
    assert gaze_dict['gaze'][1][1] == 0.6

    # Check that logging to a file worked as well
    df = pd.read_csv(fname, sep='\t')

    # We need to format the strings of tuples to an appropriate format
    arr_left_bad_fmt = df['left_gaze_point_on_display_area'].to_numpy()
    # ast.literal_eval is safe: https://stackoverflow.com/a/21735907/5201771
    arr_left = np.asarray([ast.literal_eval(i) for i in arr_left_bad_fmt])

    arr_right_bad_fmt = df['right_gaze_point_on_display_area'].to_numpy()
    arr_right = np.asarray([ast.literal_eval(i) for i in arr_right_bad_fmt])

    np.testing.assert_array_equal(arr_left, np.array(((0.3, 0), (0, 0.4))))
    np.testing.assert_array_equal(arr_right, np.array(((0.7, 0), (0, 0.6))))

    # clean up
    os.remove(fname)
