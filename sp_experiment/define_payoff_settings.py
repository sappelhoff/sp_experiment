"""Provide the payoff settings to be used in the Sampling Paradigm.

main file: sp.py

For more information, see also the following keys within
define_variable_meanings.make_events_json_dict: action_type, action, outcome

"""
import itertools
from collections import OrderedDict

import numpy as np
import pandas as pd

from sp_experiment.define_ttl_triggers import provide_trigger_dict


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
    # Get all possible combinations for two payoff distributions
    # (36*9)**2 ... i.e., 36 magnitudes*9 probabilites
    # to the power of two
    two_distrs = np.empty(((36*9)**2, 8))
    two_distrs[:] = np.nan
    for i in range(len(single_distr)):
        __ = np.roll(single_distr, shift=i, axis=0)
        data = list(zip(__, single_distr))
        two_distrs[i*len(single_distr):(1+i)*len(single_distr),
                   :] = np.array(data).reshape(-1, 8)

    # Select a subset of distributions from all those that are possible
    # =================================================================
    # Calculate the expected value of each payoff distribution
    # then select payoff distribution settings based on difference
    # between EVs ... for example, only equal payoff distribution settings
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

    # Take another subset of payoff distributions: no "dominated options"
    # ===================================================================
    # remove settings where one distribution has both options with higher
    # outcomes, for example: 6 and 7 versus 8 and 9
    # NOTE: For a low enough `ev_diff` parameter, there should be no "dominated
    #       options" anyways, according to how we computed the settings
    deletion_mask = np.ones(payoff_settings.shape[0])
    for idx, row in enumerate(payoff_settings):
        if row[0] > row[4] and row[0] > row[5]:
            if row[1] > row[4] and row[1] > row[5]:
                deletion_mask[idx] = 1
        elif row[0] < row[4] and row[0] < row[5]:
            if row[1] < row[4] and row[1] < row[5]:
                deletion_mask[idx] = 1

    deletion_mask = deletion_mask == 1
    payoff_settings = payoff_settings[deletion_mask, :]

    return payoff_settings


def get_random_payoff_dict(payoff_settings, pseudorand=False, df=None):
    """Given an array of possible payoff settings, get a random setting.

    Parameters
    ----------
    payoff_settings : ndarray, shape (n, 8)
        Subset of all possible payoff distribution settings.

    pseudorand : bool
        If True, make a random pick of payoff settings, where the currently
        least presented outcome is present. You must specify the df argument
        if True. Defauls to False.

    df : pd.DataFrame | None
        The data to be supplied if pseudorand is True. Defaults to None.

    Returns
    -------
    payoff_dict : collections.OrderedDict
        Dict with keys [0, 1] and each key containing as values a list of
        possible outcomes, the frequency of which corresponds to a probability.
        For example payoff_dict[0] = [0, 0, ,0 ,0, 0, 0, 0, 1, 1, 1] for a
        payoff distribution "0" that yields 1 with 30% chance, and 0 otherwise.

    payoff_settings : ndarray, shape (n, 8)
        Input settings with the row selected for the present payoff_dict
        removed.

    """
    if pseudorand:
        assert isinstance(df, pd.DataFrame)
        selected_row_idx = provide_balancing_selection(df, payoff_settings)
    else:
        n, __ = payoff_settings.shape
        selected_row_idx = np.random.randint(0, n)

    # Form a payoff dictionary from the selected setting
    payoff_setting = payoff_settings[selected_row_idx, :]
    payoff_dict = OrderedDict()
    payoff_dict[0] = [int(payoff_setting[0])] * int(payoff_setting[2]*10)
    payoff_dict[0] += [int(payoff_setting[1])] * int(payoff_setting[3]*10)
    payoff_dict[1] = [int(payoff_setting[4])] * int(payoff_setting[6]*10)
    payoff_dict[1] += [int(payoff_setting[5])] * int(payoff_setting[7]*10)

    # Remore the selected setting from all settings (no replacement)
    payoff_settings = np.delete(payoff_settings, [selected_row_idx], axis=0)
    return payoff_dict, payoff_settings


def provide_balancing_selection(df, payoff_settings):
    """Provide index for setting containing little sampled stimuli.

    Given the previously recorded data, find which stimuli have been presented
    only few times and then return an index into payoff_settings that will
    resolve to a setting containing such a little sampled stimulus. Here,
    stimuli are the numbers 1 to 9, as well as the side they appear on, so
    18 distinct stimulus classes.

    Parameters
    ----------
    payoff_settings : ndarray, shape (n, 8)
        Subset of all possible payoff distribution settings.

    df : pd.DataFrame | None
        The data collected until this point.

    Returns
    -------
    selected_row_idx : int
        The row index of the payoff_settings that should be picked to balance
        the currently presented stimuli.

    """
    # Get sampling actions and corresponding outcomes so far
    trig_dict = provide_trigger_dict()
    trig_sample = [ord(trig_dict['trig_left_choice']),
                   ord(trig_dict['trig_right_choice'])]
    trig_out = [ord(trig_dict['trig_show_out_l']),
                ord(trig_dict['trig_show_out_r'])]
    actions = df[df['value'].isin(trig_sample)]['action'].to_numpy(copy=True,
                                                                   dtype=int)
    outcomes = df[df['value'].isin(trig_out)]['outcome'].to_numpy(copy=True,
                                                                  dtype=int)

    # combine actions and outcomes to code outcomes on the left with negative
    # sign outcomes on the right with positive sign ... will end up with stim
    # classes
    stim_classes = outcomes * (actions*2-1)

    # Make a histogram of which stimulus_classes we have collected so far
    bins = np.hstack((np.arange(-9, 0), np.arange(1, 11)))
    stim_class_hist = np.histogram(stim_classes, bins)

    # Make an array from the hist and sort it
    stim_class_arr = np.vstack((stim_class_hist[0], stim_class_hist[1][:-1])).T
    stim_class_arr_sorted = stim_class_arr[stim_class_arr[:, 0].argsort()]

    # From what we have seen so far, take the stim_classes we have seen least
    # as priotities to be shown
    stim_to_show_i = 0
    stim_to_show = stim_class_arr_sorted[stim_to_show_i, 1]

    # Now start to look in our payoff settings, which potential settings
    # contain the stimulus class to be shown
    while True:
        number = np.abs(stim_to_show)
        side = np.sign(stim_to_show)

        # Select only payoff settings that contain the specific number
        num_select = payoff_settings[(payoff_settings ==
                                      number).any(axis=1), :]

        # From the number specific selection, select only where the number is
        # on a specific side
        if side == -1:
            num_side_select = num_select[np.where(num_select ==
                                                  number)[1] <= 1, :]
        else:
            num_side_select = num_select[np.where(num_select ==
                                                  number)[1] > 1, :]

        # If we found some candidates, return the selection for a random pick
        # from it
        if num_side_select.shape[0] > 0:
            break

        # Else, take the next simulus to be shown in line and try to find a
        # selection
        stim_to_show_i += 1
        if stim_to_show_i == stim_to_show.shape[0]:
            # This should never happen ...
            raise RuntimeError('We have run out of potential stimuli to show.')
        else:
            stim_to_show = stim_class_arr_sorted[stim_to_show_i, 1]

    # Now we have the selection of payoff_settings and we can pick a random
    # row from our selection
    n, __ = num_side_select.shape
    num_side_select_idx = np.random.randint(0, n)
    selected_row = num_side_select[num_side_select_idx]

    # And find the index into the payoff_settings
    selected_row_idx = np.where((payoff_settings ==
                                 selected_row).all(axis=1))[0][0]

    return selected_row_idx
