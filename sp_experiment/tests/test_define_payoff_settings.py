"""Testing the setup of the payoff distributions."""
import numpy as np

from sp_experiment.define_payoff_settings import (get_payoff_settings,
                                                  get_random_payoff_dict
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
