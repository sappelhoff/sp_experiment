"""Provide the payoff distributions to be used in the Sampling Paradigm.

main file: sp.py

For more information, see also the following keys within the
"task-sp_events.json" file: action_type, action, outcome

"""
import itertools

import numpy as np


def get_payoff_settings(ev_diff):
    """Provide a set of possible payoff distributions.

    For two payoff distributions with two outcomes each, provide settings in
    the form of an array, where each row is a setting for the two payoff
    distributions and the meaning of the columns is as follows: outcome 1.1,
    outcome 1.2, probability 1.1, probability 1.2, outcome 2.1, outcome 2.2,
    probability 2.1, probability 2.2.

    Parameters
    ----------
    ev_diff : float
        "Expected value difference". The difference in expected value between
        the two payoff distributions that we want for each setting.

    Returns
    -------
    payoff_settings : ndarray, shape (n, 8)
        Subset of all possible payoff distribution settings.

    """
    # Define the numbers we are working with for the probabilities of the
    # outcomes, and their magnitudes.
    initial_probs = np.arange(0.1, 1, 0.1)
    initial_mags = np.arange(1, 10)

    # Get all possible settings for a single distribution of two outcomes
    # ===================================================================
    # For single distribution, we have two possible outcomes. Take k unordered
    # outcomes from n possibilities; the number is given by binomial
    # coefficient:
    # np.math.factorial(n) / (np.math.factorial(k)*np.math.factorial(n-k))
    k = 2
    single_mags = np.array(list(itertools.combinations(initial_mags, k)))

    # Now map each possible magnitude combination to all probability
    # combinations. Example: magnitudes [1,2] can be obtained with
    # probabilities [0.1, 0.9] or with probabilities [0.9, 0.1], ...
    single_probs = np.array(list(zip(initial_probs, 1 - initial_probs)))

    mags = np.repeat(single_mags,
                     repeats=len(single_probs),
                     axis=0)

    probs = np.tile(single_probs, reps=(len(single_mags), 1))

    # single payoff distribution array: each row is a possible setting of
    # dimensions: magnitude1, magnitude2, probability1, probability2
    single_distr = np.concatenate((mags, probs), axis=1)

    # Get all possible settings for two distributions
    # ===============================================
    # Get all possible combinations for two urns
    # (36*9)**2 ... i.e., 36 magnitudes*9 probabilites
    # to the power of two
    two_distrs = np.empty(((36*9)**2, 8)) * np.nan
    for i in range(len(single_distr)):
        __ = np.roll(single_distr, shift=i, axis=0)
        data = list(zip(__, single_distr))
        two_distrs[i*len(single_distr):(1+i)*len(single_distr),
                   :] = np.array(data).reshape(-1, 8)

    # Select a subset of distributions from all those that are possible
    # =================================================================
    # Calculate the expected value of each urn
    # then select urn settings based on difference
    # between EVs ... for example, only equal urn settings
    # Or where the difference is >0, but <1
    evs = list()
    for row in two_distrs:
        ev1 = row[0]*row[2] + row[1]*row[3]
        ev2 = row[4]*row[6] + row[5]*row[7]
        evs.append(np.abs(ev1-ev2))

    # sanity check, then use as array (round to 14 decimals to avoid weird
    # floating point arithmetic)
    assert not np.isnan(two_distrs).all()
    evs = np.round(np.array(evs), 14)

    # Now we make use of the expected value difference that was set as a
    # parameter to the function call, to determine which subset of possible
    # payoff distribution setttings we want.
    ev_payoff_settings = two_distrs[np.where(evs == ev_diff)]
    ev_payoff_settings = np.round(ev_payoff_settings, 14)

    # Take subset of payoff distribtions: only if we have 4 distinct outcomes
    # =======================================================================
    payoff_settings = None
    for row in ev_payoff_settings:
        if len(np.unique(row[[0, 1, 4, 5]])) == 4:
            if payoff_settings is None:
                payoff_settings = np.expand_dims(row, axis=0)
            else:
                payoff_settings = np.concatenate((payoff_settings,
                                                  np.expand_dims(row, 0)),
                                                 axis=0)

    return payoff_settings


def get_random_payoff_dict(payoff_settings):
    """Given an array of possible payoff settings, get a random setting.

    Parameters
    ----------
    payoff_settings : ndarray, shape (n, 8)
        Subset of all possible payoff distribution settings.

    Returns
    -------
    payoff_dict : dict
        Dict with keys [0, 1] and each key containing as values a list of
        possible outcomes, the frequency of which corresponds to a probability.
        For example payoff_dict[0] = [0, 0, ,0 ,0, 0, 0, 0, 1, 1, 1] for a
        payoff distribution "0" that yields 1 with 30% chance, and 0 otherwise.

    payoff_settings : ndarray, shape (n, 8)
        Input settings with the row selected for the present payoff_dict
        removed.
    """
    n, __ = payoff_settings.shape
    selected_row = np.random.randint(0, n)

    # Form a payoff dictionary from the selected setting
    payoff_setting = payoff_settings[selected_row, :]
    payoff_dict = dict()
    payoff_dict[0] = [int(payoff_setting[0])] * int(payoff_setting[2]*10)
    payoff_dict[0] += [int(payoff_setting[1])] * int(payoff_setting[3]*10)
    payoff_dict[1] = [int(payoff_setting[4])] * int(payoff_setting[6]*10)
    payoff_dict[1] += [int(payoff_setting[5])] * int(payoff_setting[7]*10)

    # Remore the selected setting from all settings (no replacement)
    payoff_settings = np.delete(payoff_settings, [selected_row], axis=0)

    return payoff_dict, payoff_settings
