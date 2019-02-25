"""Testing the utility functions."""
import os
import os.path as op
from tempfile import gettempdir
from shutil import rmtree


import pytest
import numpy as np
import pandas as pd

import sp_experiment
from sp_experiment.utils import (Fake_serial,
                                 get_final_choice_outcomes,
                                 get_payoff_dict,
                                 get_passive_action,
                                 get_passive_outcome,
                                 get_jittered_waitframes,
                                 utils_fps,
                                 log_data
                                 )
from sp_experiment.define_payoff_settings import (get_payoff_settings,
                                                  get_random_payoff_dict
                                                  )
init_dir = op.dirname(sp_experiment.__file__)
test_data_dir = op.join(init_dir, 'tests', 'data')


def test_Fake_serial():
    """Test the Fake_serial class."""
    ser = Fake_serial()
    ser.write(1)
    assert True


def test_get_final_choice_outcomes():
    """Test getting final choice outcomes."""
    fname = '2_trials_no_errors.tsv'
    fpath = op.join(test_data_dir, fname)
    df = pd.read_csv(fpath, sep='\t')
    outcomes = get_final_choice_outcomes(df)
    expected_outcomes = [8, 6]  # as can be read in the data file
    np.testing.assert_array_equal(outcomes, expected_outcomes)


def test_get_payoff_dict():
    """Test getting payoff_dicts."""
    fname = '2_trials_no_errors.tsv'
    fpath = op.join(test_data_dir, fname)
    df = pd.read_csv(fpath, sep='\t')

    # The trial argument is 0-indexed
    payoff_dict = get_payoff_dict(df, 0)
    assert isinstance(payoff_dict, dict)

    # Make a more thorough test with the second payoff distribution
    payoff_dict = get_payoff_dict(df, 1)
    read_set = set(payoff_dict[0])
    expected_set = set((1, 6))
    assert len(read_set) == len(expected_set)
    assert sorted(read_set) == sorted(expected_set)

    read_set = set(payoff_dict[1])
    expected_set = set((9, 5))
    assert len(read_set) == len(expected_set)
    assert sorted(read_set) == sorted(expected_set)

    # There were only 2 trials, this should be out of index
    with pytest.raises(IndexError):
        get_payoff_dict(df, 2)


def test_get_passive_action():
    """Test getting an action for replay in passive condition."""
    fname = '2_trials_no_errors.tsv'
    fpath = op.join(test_data_dir, fname)
    df = pd.read_csv(fpath, sep='\t')

    keys_rts = get_passive_action(df, 0, 0)

    # keys_rts should be a list of tuples
    assert isinstance(keys_rts, list)
    assert len(keys_rts) == 1
    assert isinstance(keys_rts[0], tuple)

    # did we read the correct numbers
    assert keys_rts[0][0] == 'right'
    np.testing.assert_allclose(keys_rts[0][1], 0.328, rtol=0.01)


def test_get_passive_outcome():
    """Test getting an outcome for replay in passive condition."""
    fname = '2_trials_no_errors.tsv'
    fpath = op.join(test_data_dir, fname)
    df = pd.read_csv(fpath, sep='\t')

    # If we pass the "last sample", we get the final choice outcome
    outcome = get_passive_outcome(df, 0, -1)
    outcomes = get_final_choice_outcomes(df)
    assert outcome == outcomes[0]

    # Other samples give us reasonable results
    expected_outcomes = [2, 8, 8, 8, 3, 3, 3, 3, 3, 3, 3, 3]
    for sample, expected in zip(range(12), expected_outcomes):
        out = get_passive_outcome(df, 0, sample)
        assert out == expected


def test_get_jittered_waitframes():
    """Test the waitframes func."""
    n = 100
    for i in range(n):
        wait_frames = get_jittered_waitframes(1000, 2000)
        assert wait_frames >= utils_fps and wait_frames <= utils_fps*2


def test_log_data():
    """Sanity check the data logging."""
    fname = '2_trials_no_errors.tsv'
    fpath = op.join(test_data_dir, fname)
    df = pd.read_csv(fpath, sep='\t')

    # Check that action_types are as expected
    action_types = df['action_type'].dropna().unique().tolist()
    np.testing.assert_array_equal(action_types,
                                  ['sample', 'stop', 'final_choice'])

    # Create a temporary logging file
    data_dir = op.join(gettempdir(), '.{}'.format(hash(os.times())))
    os.makedirs(data_dir)
    fname = 'tmp_data_file.tsv'
    fpath = op.join(data_dir, fname)

    # Log some data
    log_data(fpath)

    with open(fpath, 'r') as fin:
        for i, line in enumerate(fin.readlines()):
            # spot check some known data in the line
            assert line.strip().split('\t')[-1] == '0'

        # There should have been only one line
        assert i == 0

    # Log more data
    log_data(fpath, action=5)
    log_data(fpath, action=2)
    log_data(fpath, action=3)
    log_data(fpath, action=7)

    df = pd.read_csv(fpath, sep='\t', header=None)

    action_types = df[3].tolist()
    action_vals = df[4].tolist()
    assert len(action_types) == 5 and len(action_vals) == 5
    assert np.isnan(action_types[0]) and np.isnan(action_vals[0])
    assert action_types[1] == 'forced_stop' and action_vals[1] == 0
    assert action_types[2] == 'stop' and action_vals[2] == 2
    assert action_types[3] == 'final_choice' and action_vals[3] == 0
    assert action_types[4] == 'premature_stop' and action_vals[4] == 2

    # And even more data logging
    payoff_settings = get_payoff_settings(0.1)
    payoff_dict, payoff_settings = get_random_payoff_dict(payoff_settings)
    log_data(fpath, payoff_dict=payoff_dict)

    # Remove the temporary dir and all its contents
    rmtree(data_dir, ignore_errors=True)
