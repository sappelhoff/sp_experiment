"""Testing the utility functions."""
import time
import os
import os.path as op
from tempfile import gettempdir
from shutil import rmtree, copyfile
from collections import OrderedDict

import pytest
import numpy as np
import pandas as pd

import sp_experiment
from sp_experiment.define_settings import (EXPECTED_FPS,
                                           KEYLIST_SAMPLES
                                           )
from sp_experiment.utils import (Fake_serial,
                                 My_serial,
                                 calc_bonus_payoff,
                                 get_final_choice_outcomes,
                                 get_payoff_dict_from_df,
                                 get_passive_action,
                                 get_passive_outcome,
                                 get_jittered_waitframes,
                                 log_data
                                 )
from sp_experiment.define_payoff_settings import (get_payoff_settings,
                                                  get_payoff_dict
                                                  )
init_dir = op.dirname(sp_experiment.__file__)
data_dir = op.join(init_dir, 'experiment_data')
test_data_dir = op.join(init_dir, 'tests', 'data')

no_errors_file = op.join(test_data_dir, '2_trials_no_errors.tsv')


def test_serials():
    """Test the Fake_serial class."""
    some_byte = bytes([1])
    ser = Fake_serial()
    assert ser.write(some_byte) == some_byte

    # Also covers "mysleep"
    waitsecs = 1
    ser = My_serial(ser, waitsecs)
    start = time.perf_counter()
    ser.write(some_byte)
    stop = time.perf_counter()
    assert (stop - start) >= waitsecs


def test_calc_bonus_payoff():
    """Test bonus calculation."""
    # Check for non-present data
    bonus = calc_bonus_payoff(998)
    assert isinstance(bonus, list)
    assert len(bonus) == 4
    assert bonus[0] == 'did not yet complete task "A".'

    bonus = calc_bonus_payoff(999)
    assert bonus[1] == 'did not yet complete task "B".'

    # present data ... temporarily copy over a test file
    tmp_fpath1 = op.join(data_dir, 'sub-998_task-spactive_events.tsv')
    tmp_fpath2 = op.join(data_dir, 'sub-998_task-sppassive_events.tsv')
    copyfile(no_errors_file, tmp_fpath1)
    copyfile(no_errors_file, tmp_fpath2)

    bonus = calc_bonus_payoff(998, exchange_rate=0.1)

    # remove tmp files
    os.remove(tmp_fpath1)
    os.remove(tmp_fpath2)
    assert bonus[-1] == '4 Euros'


def test_get_final_choice_outcomes():
    """Test getting final choice outcomes."""
    df = pd.read_csv(no_errors_file, sep='\t')
    outcomes = get_final_choice_outcomes(df)
    expected_outcomes = [5, 9]  # as can be read in the data file
    np.testing.assert_array_equal(outcomes, expected_outcomes)


def test_get_payoff_dict_from_df():
    """Test getting payoff_dicts."""
    df = pd.read_csv(no_errors_file, sep='\t')

    # The trial argument is 0-indexed
    payoff_dict = get_payoff_dict_from_df(df, 0)
    assert isinstance(payoff_dict, OrderedDict)

    # Make a more thorough test with the second payoff distribution
    payoff_dict = get_payoff_dict_from_df(df, 1)
    read_set = set(payoff_dict[0])
    expected_set = set((3, 9))
    assert len(read_set) == len(expected_set)
    assert sorted(read_set) == sorted(expected_set)

    read_set = set(payoff_dict[1])
    expected_set = set((7, 8))
    assert len(read_set) == len(expected_set)
    assert sorted(read_set) == sorted(expected_set)

    # There were only 2 trials, this should be out of index
    with pytest.raises(IndexError):
        get_payoff_dict_from_df(df, 2)


def test_get_passive_action():
    """Test getting an action for replay in passive condition."""
    df = pd.read_csv(no_errors_file, sep='\t')

    keys_rts = get_passive_action(df, 0, 0)

    # keys_rts should be a list of tuples
    assert isinstance(keys_rts, list)
    assert len(keys_rts) == 1
    assert isinstance(keys_rts[0], tuple)

    # did we read the correct numbers
    assert keys_rts[0][0] == KEYLIST_SAMPLES[0]
    np.testing.assert_allclose(keys_rts[0][1], 0.227, rtol=0.01)


def test_get_passive_outcome():
    """Test getting an outcome for replay in passive condition."""
    df = pd.read_csv(no_errors_file, sep='\t')

    # If we pass the "last sample", we get the final choice outcome
    outcome = get_passive_outcome(df, 0, -1)
    outcomes = get_final_choice_outcomes(df)
    assert outcome == outcomes[0]

    # Other samples give us reasonable results
    expected_outcomes = [3, 3, 3, 5, 5, 5, 4, 5, 3, 3, 3, 3]
    for sample, expected in zip(range(12), expected_outcomes):
        out = get_passive_outcome(df, 0, sample)
        assert out == expected


def test_get_jittered_waitframes():
    """Test the waitframes func."""
    n = 100
    for _ in range(n):
        wait_frames = get_jittered_waitframes(1000, 2000)
        assert wait_frames >= EXPECTED_FPS and wait_frames <= EXPECTED_FPS*2


def test_log_data():
    """Sanity check the data logging."""
    df = pd.read_csv(no_errors_file, sep='\t')

    # Check that action_types are as expected
    action_types = df['action_type'].dropna().unique().tolist()
    np.testing.assert_array_equal(action_types,
                                  ['sample', 'forced_stop', 'final_choice'])

    # Create a temporary logging file
    myhash = str(hash(os.times()))
    data_dir = op.join(gettempdir(), myhash)
    os.makedirs(data_dir)
    fname = 'tmp_data_file.tsv'
    fpath = op.join(data_dir, fname)

    # Log some data
    log_data(fpath)

    with open(fpath, 'r') as fin:
        for i, line in enumerate(fin.readlines()):
            # spot check some known data in the line
            assert line.strip().split('\t')[-2] == '0'

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
    setting = payoff_settings[0, :]
    payoff_dict = get_payoff_dict(setting)
    log_data(fpath, payoff_dict=payoff_dict)

    # Remove the temporary dir and all its contents
    rmtree(data_dir, ignore_errors=True)
