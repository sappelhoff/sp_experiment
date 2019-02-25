"""Testing the setup of the payoff distributions."""
import numpy as np

from sp_experiment.define_payoff_settings import (get_payoff_settings,
                                                  get_random_payoff_dict,
                                                  shuffle_left_right
                                                  )


def test_get_payoff_settings():
    """Test the setup of payoff distributions."""
    payoff_settings = get_payoff_settings(0.1)
    assert payoff_settings.ndim == 2
    assert payoff_settings.shape[-1] == 8
    assert payoff_settings.shape[0] >= 1
    for probability in payoff_settings[0, [2, 3, 6, 7]]:
        assert probability in np.round(np.arange(0.1, 1, 0.1), 1)
    for magnitude in payoff_settings[0, [0, 1, 4, 5]]:
        assert magnitude in range(1, 10)


def test_get_random_payoff_dict():
    """Test getting a payoff_dict off a setup."""
    payoff_settings = get_payoff_settings(0.1)
    payoff_dict, payoff_settings = get_random_payoff_dict(payoff_settings)
    assert isinstance(payoff_dict, dict)


def test_shuffle_left_right():
    """Test that we can shuffle values of a dict."""
    d = {0: [1, 2, 3], 1: [4, 5, 6]}
    n = 100
    was_shuffled = False
    for i in range(n):
        d_new = shuffle_left_right(d)
        # Assert the order of keys is stable after each shuffle
        np.testing.assert_array_equal(np.fromiter(d.keys(), int),
                                      np.fromiter(d_new.keys(), int))

        # Over the n shuffles, we should experience a switch of values at least
        # once
        vals_0 = np.asarray(d_new[0])
        if np.array_equal(vals_0, d[1]):
            was_shuffled = True

    assert was_shuffled
