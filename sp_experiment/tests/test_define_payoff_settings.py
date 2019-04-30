"""Testing the setup of the payoff distributions."""
import os.path as op
from collections import OrderedDict

import numpy as np
import pandas as pd

import sp_experiment
from sp_experiment.define_payoff_settings import (get_payoff_settings,
                                                  get_random_payoff_dict,
                                                  )


def test_get_payoff_settings():
    """Test the setup of payoff distributions."""
    payoff_settings = get_payoff_settings(0.1)
    assert payoff_settings.ndim == 2
    assert payoff_settings.shape[-1] == 8
    assert payoff_settings.shape[0] >= 1
    for probability in payoff_settings[0, [2, 3, 6, 7]]:
        assert probability in np.round(np.arange(0.1, 1, 0.1), 1)
    mags = list()
    for magnitude in payoff_settings[0, [0, 1, 4, 5]]:
        assert magnitude in range(1, 10)
        mags.append(magnitude)
    assert len(np.unique(mags)) == 4


def test_get_random_payoff_dict():
    """Test getting a payoff_dict off a setup."""
    payoff_settings = get_payoff_settings(0.1)
    n_settings = payoff_settings.shape[0]
    payoff_dict, payoff_settings = get_random_payoff_dict(payoff_settings)

    # Should be a dict
    assert isinstance(payoff_dict, OrderedDict)
    assert len(list(payoff_dict.values())[0]) == 10
    assert len(list(payoff_dict.values())[1]) == 10

    # Payoff settings should have been decreased by one
    assert payoff_settings.shape[0] == (n_settings - 1)

    # Also test with a pseudorandom draw
    init_dir = op.dirname(sp_experiment.__file__)
    test_data_dir = op.join(init_dir, 'tests', 'data')
    fname = '2_trials_no_errors.tsv'
    fpath = op.join(test_data_dir, fname)
    df = pd.read_csv(fpath, sep='\t')
    payoff_dict, payoff_settings = get_random_payoff_dict(payoff_settings,
                                                          pseudorand=True,
                                                          df=df)
