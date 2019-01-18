"""Testing the utility functions."""
import os.path as op

import numpy as np
import pandas as pd

import sp_experiment
from sp_experiment.utils import (Fake_serial,
                                 get_final_choice_outcomes
                                 )

init_dir = op.dirname(sp_experiment.__file__)
test_data_dir = op.join(init_dir, 'tests', 'data')


def test_Fake_serial():
    ser = Fake_serial()
    ser.write(1)
    assert True


def test_get_final_choice_outcomes():
    fname = '2_trials_no_errors.tsv'
    fpath = op.join(test_data_dir, fname)
    df = pd.read_csv(fpath, sep='\t')
    outcomes = get_final_choice_outcomes(df)
    expected_outcomes = [8, 6]  # as can be read in the data file
    np.testing.assert_array_equal(outcomes, expected_outcomes)
