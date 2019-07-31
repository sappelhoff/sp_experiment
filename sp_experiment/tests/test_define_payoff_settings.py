"""Testing the setup of the payoff distributions."""
import os.path as op
from collections import OrderedDict

import numpy as np
import pandas as pd

import sp_experiment
from sp_experiment.define_payoff_settings import (get_payoff_settings,
                                                  get_random_payoff_dict,
                                                  get_random_payoff_settings
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

    # Test rng seed setting
    payoff_settings = get_payoff_settings(0.9)
    n_settings = payoff_settings.shape[0]
    payoff_dict1, _ = get_random_payoff_dict(payoff_settings)
    payoff_dict2, _ = get_random_payoff_dict(payoff_settings)
    assert payoff_dict1 != payoff_dict2
    payoff_dict3, _ = get_random_payoff_dict(payoff_settings, seed=1)
    payoff_dict4, _ = get_random_payoff_dict(payoff_settings, seed=1)
    assert payoff_dict3 == payoff_dict4
    payoff_dict5, _ = get_random_payoff_dict(payoff_settings, seed=2)
    assert payoff_dict4 != payoff_dict5


def _simulate_run(rand_payoff_settings, n_samples= 12, seed=None):
    """Simulate a participant with 50% 50% left right tendency."""
    rng = np.random.RandomState(seed)
    actions = list()
    outcomes = list()
    for setting in rand_payoff_settings:
        payoff_dict = get_payoff_dict(setting)
        for sample in range(n_samples):
            action = rng.choice((0, 1))
            actions.append(action)
            outcome = rng.choice(payoff_dict[action])
            outcomes.append(outcome)

    actions = np.array(actions)
    outcomes = np.array(outcomes)
    # combine actions and outcomes to code outcomes on the left with negative
    # sign outcomes on the right with positive sign ... will end up with stim
    # classes: - sign for "left", + sign for "right"
    stim_classes = outcomes * (actions*2-1)

    return stim_classes


def _make_class_hist(stim_classes):
    """Turn stim_classes into hist."""
    # Make a histogram of which stimulus_classes we have collected so far
    bins = np.hstack((np.arange(-9, 0), np.arange(1, 11)))
    stim_class_hist = np.histogram(stim_classes, bins)

    # Make an array from the hist and sort it
    stim_class_arr = np.vstack((stim_class_hist[0], stim_class_hist[1][:-1])).T
    stim_class_arr_sorted = stim_class_arr[stim_class_arr[:, 0].argsort()]

    return stim_class_arr_sorted


def test_balancing():
    """Test that we can get a balanced stimulus selection."""
    seed = 1
    max_ntrls = 100
    ev_diff = 0.9
    payoff_settings = get_payoff_settings(ev_diff)


    # No balancing at all, this will lead to a few stim_classes never
    # being shown
    rand_payoff_settings = payoff_settings.copy()
    rng = np.random.RandomState(seed)
    perm = rng.permutation(max_ntrls)
    rand_payoff_settings = rand_payoff_settings[perm, :]
    stim_classes = _simulate_run(rand_payoff_settings, n_samples=12, seed=seed)
    hist = _make_class_hist(stim_classes)
    diff1 = np.diff(hist[[0, -1], 0])

    # some balancing
    rand_payoff_settings = get_random_payoff_settings(max_ntrls,
                                                      payoff_settings,
                                                      -1
                                                      seed)
    stim_classes = _simulate_run(rand_payoff_settings, n_samples=12, seed=seed)
    hist = _make_class_hist(stim_classes)
    diff2 = np.diff(hist[[0, -1], 0])

    # Most balancing
    rand_payoff_settings = get_random_payoff_settings(max_ntrls,
                                                      payoff_settings,
                                                      0.6
                                                      seed)
    stim_classes = _simulate_run(rand_payoff_settings, n_samples=12, seed=seed)
    hist = _make_class_hist(stim_classes)
    diff3 = np.diff(hist[[0, -1], 0])

    assert diff1 > diff2
    assert diff2 > diff3
