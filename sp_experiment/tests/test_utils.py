"""Testing the utility functions."""
import os.path as op

import pytest
import numpy as np
import pandas as pd

import sp_experiment
from sp_experiment.utils import (Fake_serial,
                                 get_final_choice_outcomes,
                                 get_payoff_dict,
                                 get_passive_action,
                                 get_passive_outcome
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


def test_log_data():
    """Sanity check the data logging."""
    fname = '2_trials_no_errors.tsv'
    fpath = op.join(test_data_dir, fname)
    df = pd.read_csv(fpath, sep='\t')

    # Check that action_types are as expected
    action_types = df['action_type'].dropna().unique().tolist()
    np.testing.assert_array_equal(action_types,
                                  ['sample', 'stop', 'final_choice'])
