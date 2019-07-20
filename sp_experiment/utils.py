"""Provide utility functions for the main experiment.

Only functions that do not need a direct psychopy import.

main file: sp.py

other utilities: psychopy_utils.py

"""
import os.path as op
from collections import OrderedDict
from time import perf_counter

import numpy as np
import pandas as pd
import tobii_research as tr

import sp_experiment
from sp_experiment.define_payoff_settings import get_random_payoff_dict
from sp_experiment.define_ttl_triggers import provide_trigger_dict
from sp_experiment.define_settings import (KEYLIST_SAMPLES,
                                           EXPECTED_FPS
                                           )


class Fake_serial():
    """Convenience class to run the code without true serial connection."""

    def write(self, byte):
        """Take a byte and do nothing."""
        pass


class My_serial():
    """Convenience class that always resets the event marker to zero."""

    def __init__(self, ser, waitsecs):
        """Initialize the class.

        Parameters
        ----------
        ser : serial.Serial
            A serial port object
        waitsecs : float
            Time in seconds to wait until resetting the serial port to zero

        """
        self.ser = ser
        self.waitsecs = waitsecs
        self.reset_val = bytes([0])

    def write(self, byte):
        """Take a byte, write it, and reset to zero."""
        self.ser.write(byte)
        mysleep(self.waitsecs)
        self.ser.write(self.reset_val)


def mysleep(waitsecs):
    """Block execution of further code for `waitsecs` seconds."""
    twaited = 0
    start = perf_counter()
    while twaited < waitsecs:
        twaited = perf_counter() - start


def calc_bonus_payoff(sub_id, exchange_rate=0.01, lang='en'):
    """Calculate the bonus money a participant has earned.

    Parameters
    ----------
    sub_id : int
        The subject ID
    exchange_rate : float
        Converting points to Euros
    lang : str
        Language, can be 'de' or 'en' for German or English.

    Returns
    -------
    bonus : list of str
        A list containing strings for each condition with the bonus in Euros,
        or that a condition has not yet been completed.

    """
    data_dir = op.join(op.dirname(sp_experiment.__file__), 'experiment_data')
    bonus = list()
    total_money = list()
    # Check how much was earned in each task
    for condition in ['active', 'passive', 'description']:
        if condition == 'description':
            fname = 'sub-{:02d}_task-description_events.tsv'.format(sub_id)
        else:
            fname = 'sub-{:02d}_task-sp{}_events.tsv'.format(sub_id, condition)
        fpath = op.join(data_dir, fname)

        # In case task was not done, tell it so
        if not op.exists(fpath):
            if condition == 'active':
                modstr = 'A'
            elif condition == 'passive':
                modstr = 'B'
            else:
                modstr = 'C'
            if lang == 'de':
                bonus_str = ('Aufgabe "{}" wurde noch nicht durchgeführt.'
                             .format(modstr))
            elif lang == 'en':
                bonus_str = 'did not yet complete task "{}".'.format(modstr)

            # Task not done, means no money earned
            total_money.append(0)

        # If task was done, get all earned points
        else:
            df = pd.read_csv(fpath, sep='\t')
            trig_dict = provide_trigger_dict()
            trig_fin_out = [ord(trig_dict['trig_show_final_out_l']),
                            ord(trig_dict['trig_show_final_out_r'])]
            vals = df[df['value'].isin(trig_fin_out)]['outcome'].values
            points = np.sum(vals)

            # Convert points to money for this task
            money = int(np.ceil(points * exchange_rate))
            if lang == 'de':
                bonus_str = '{} Euro wurden als Bonus verdient.'.format(money)
            elif lang == 'en':
                bonus_str = 'earned {} Euros as bonus.'.format(money)

            # keep a tally for computing total later on
            total_money.append(money)

        # append this task's bonus to all bonus_strs
        bonus.append(bonus_str)

    # make one more str for TOTAL
    total = np.sum(total_money)
    bonus_str = '{} Euros'.format(total)
    bonus.append(bonus_str)

    return bonus


def get_final_choice_outcomes(df):
    """Get a vector of the final choice outcomes.

    Parameters
    ----------
    df : pandas.DataFrame
        Data that was collected

    Returns
    -------
    outcomes : ndarray
        vector of outcomes final choices.

    """
    trial_list = [int(i) for i in df['trial'].dropna().unique()]
    outcomes = list()
    for trial in trial_list:
        tmp_df = df[df['trial'] == trial]
        # The last outcome recorded in a trial is final choice outcome
        outcomes.append(tmp_df['outcome'].dropna().tolist()[-1])
    outcomes = np.asarray(outcomes)

    return outcomes


def _get_payoff_setting(df, trial, experienced=False):
    """Get the payoff setting.

    Get the setting and reformat it to fit with internal usage in
    `define_payoff_settings.py`. That is, the columns are organized as:
    outcome 1.1, outcome 1.2, probability 1.1, probability 1.2, outcome 2.1,
    outcome 2.2, probability 2.1, probability 2.2.

    Parameters
    ----------
    df : pandas.DataFrame
        The data from which to obtain payoff settings.
    trial : int
        The trial within the data for which to retrieve the payoff setting.
    experienced : bool
        if True, get the experienced payoff_setting instead of the true one

    Returns
    -------
    setting : ndarray, shape(8,)

    Notes
    -----
    Always take the last available setting, because the previous ones (if there
    are any) have been dropped due to an error (if there was one)

    """
    trigger_dict = provide_trigger_dict()
    error_trig = ord(trigger_dict['trig_error'])
    df = remove_error_rows(df, error_trig)
    tmp_df = df[(df['trial'] == trial)]
    if not experienced:
        tmp_df = tmp_df.loc[:,  'mag0_1':'prob1_2'].dropna()
        # wrong format is mag, prob, mag, prob, ...
        wrong_format_setting = tmp_df.iloc[-1].tolist()

    elif experienced:
        # outcome is always 2 events after sample action
        sample_idx = tmp_df[tmp_df['action_type'] == 'sample'].index
        outcome_idx = sample_idx + 2
        sides = tmp_df.loc[sample_idx, 'action'].values
        outcomes = tmp_df.loc[outcome_idx, 'outcome'].values

        # experienced expected values for left and right option
        payoff_dict = {side: list(outcomes[sides == side]) for side in [0, 1]}

        # Calculate probabilities for each outcome
        wrong_format_setting = list()
        for side in [0, 1]:
            distr = payoff_dict[side]

            # Special case 1 if only one distr sampled: add two 99s with
            # each p=99
            if len(distr) == 0:
                for i in [99, 99, 99, 99]:
                    wrong_format_setting.append(i)
                continue

            # Special case 2 if only one outcome sampled: add a 98 with p=0
            outcomes = np.unique(distr)
            if len(outcomes) < 2:
                outcomes = np.append(outcomes, np.array(98))
            # Go though outcomes
            for out_i in outcomes:
                wrong_format_setting.append(out_i)
                # Round it to one decimal
                p = np.round(distr.count(out_i) / len(distr), 2)
                wrong_format_setting.append(p)

    # Correct format from mag, prob, mag, prob ... to mag, mag, prob, prob ...
    setting = np.array(wrong_format_setting)[[0, 2, 1, 3, 4, 6, 5, 7]]
    setting = np.expand_dims(setting, 0)

    # quick sanity check that we have proper roundings, for example 0.3 instead
    # of 0.29999999 ... 1., 2., 3., etc. would be fine (as magnitudes)
    for entry in setting[0]:
        # 2 for magnitudes, 3 or 4 for probs ... or special entry "99"
        # (experienced)
        assert (len(str(entry)) in [2, 3, 4]) or entry in [98, 99]
    return setting


def get_payoff_dict(df, trial):
    """Get the payoff dict at a trial within the data.

    Parameters
    ----------
    df : pandas.DataFrame
        Data from where to get the payoff dict
    trial : int
        Index into the data for which to fetch the payoff dict

    Returns
    -------
    payoff_dict : collections.OrderedDict
        Dictionary containing the reward distribution setting of the current
        trial. NOTE: returns the "final" payoff_dict that was used for
        drawing the reward

    """
    setting = _get_payoff_setting(df, trial)
    # NOTE: we use get_random_payoff_dict simply for putting the structure
    # into the right order. With a setting of length 1, there is no randomness
    # as to which setting gets drawn.
    payoff_dict, _ = get_random_payoff_dict(setting)
    return payoff_dict


def remove_error_rows(df, error_trig):
    """Identify error rows and remove them.

    Identify errors via an event value and discard all rows and including the
    error row within the trial that the error happened.

    Parameters
    ----------
    df : pandas.DataFrame
        The original data with a 'trial' and 'value' column
    error_trig : int
        The event value marking an error, 16 in v0.1.0, 20 in v0.2.0

    Returns
    -------
    df : pandas.DataFrame
        The original df with the trials containing errors remove

    """
    error_idx = df.index[df['value'] == error_trig].values
    error_trls = df['trial'][error_idx].values

    remove_idx = list()
    for idx, trl in zip(error_idx, error_trls):
        __ = np.logical_and(df['trial'] == trl, df.index <= idx)
        remove_idx += df.index[__].to_list()

    df = df.drop(remove_idx)
    return df


def get_passive_action(df, trial, sample):
    """Get data for a replay.

    Parameters
    ----------
    df : pandas.DataFrame
        Data to be replayed
    trial, sample : int
        Indices into the data for which to fetch actions

    Returns
    -------
    keys_rts : list of tuples
        each entry in the list contains a tuple of the pressed key and the
        reaction time associated with the keypress.

    """
    admissible_actions = ['sample', 'stop', 'forced_stop', 'premature_stop']
    df = df[(df['trial'] == trial) &
            (df['action_type'].isin(admissible_actions))]
    key = int(df['action'].tolist()[int(sample)])
    rt = float(df['response_time'].tolist()[int(sample)])
    key = OrderedDict(enumerate(KEYLIST_SAMPLES))[key]
    keys_rts = [(key, rt)]
    return keys_rts


def get_passive_outcome(df, trial, sample):
    """Get data for a replay.

    Parameters
    ----------
    df : pandas.DataFrame
        Data to be replayed
    trial, sample : int
        Indices into the data for which to fetch actions

    Returns
    -------
    outcome : int
        magnitude of the outcome to be obtained in the passive condition

    """
    df = df[(df['trial'] == trial)]
    outcomes = df[(df['trial'] == trial)]['outcome'].dropna()
    outcome = int(outcomes.tolist()[sample])
    return outcome


def get_jittered_waitframes(min_wait, max_wait, fps=EXPECTED_FPS):
    """From a uniform distribution, determine a waiting time within an interval.

    Parameters
    ----------
    min_wait, max_wait :  int
        The minimum and maximum wait time in milliseconds.
    fps : int
        Refreshrate of the screen.

    Returns
    -------
    wait_frames : int
        A wait time in frames in the interval [min_wait, max_wait]

    """
    low = int(np.floor(min_wait/1000 * fps))
    high = int(np.ceil(max_wait/1000 * fps))
    wait_frames = np.random.randint(low, high+1)
    return wait_frames


# Define action types, to be used in log_data
action_type_dict = OrderedDict()
action_type_dict[0] = 'sample'
action_type_dict[1] = 'sample'
action_type_dict[2] = 'stop'
action_type_dict[3] = 'final_choice'
action_type_dict[4] = 'final_choice'
action_type_dict[5] = 'forced_stop'
action_type_dict[6] = 'forced_stop'
action_type_dict[7] = 'premature_stop'
action_type_dict['n/a'] = 'n/a'


def log_data(fpath, onset='n/a', duration=0, trial='n/a', action='n/a',
             outcome='n/a', response_time='n/a', value='n/a',
             payoff_dict='n/a', fps=EXPECTED_FPS, deduct_onset_frames=0,
             version=sp_experiment.__version__, reset=False):
    """Write data to the log file.

    All inputs except the file path default to 'n/a'.

    Parameters
    ----------
    fpath : str
        Path to the log file.
    onset : float | 'n/a'
        onset of the event in seconds
    duration : int | 0
        duration of the event in frames. Will then be converted to seconds by
        dividing with `EXPECTED_FPS`.
    trial : int | 'n/a'
        the number of the trial in which this event happened.
    action : int, one of [1, 2, 3] | 'n/a'
        the concrete action that the subject performed for the action type
    outcome : int | 'n/a'
        the outcome that the subject received for their action
    response_time : float | 'n/a'
        the time it took the subject to respond after the onset of the event
    value : byte | 'n/a'
        the TTL trigger value (=EEG marker value) associated with an event
    payoff_dict : collections.OrderedDict | 'n/a' | np.ndarray
        Dictionary containing the reward distribution setting of the current
        trial. Can also be a numpy array of shape (8,) containing the variables
        "mag0_1, prob0_1, mag0_2, prob0_2, mag1_1, prob1_1, mag1_2, prob1_2"
    fps : int
        frames per second used in this experiment
    deduct_onset_frames : int
        number of frames to deduct from onset. For example, because the
        log_data function was called N frames later. Then we deduct N / fps
        seconds from the onset
    version : str
        version of the experiment used for collecting this data
    reset : bool
        if True, discard all prior events in the current trial because of
        an error of the participant. If False, ignore it

    See also
    --------
    define_variable_meanings.make_events_json_dict

    """
    # Infer action type
    action_type = action_type_dict[action]
    if action in [5, 6]:
        action = action - 5
    elif action == 7:
        action = 2
    elif action != 'n/a':
        action = (action - 3) if action in [3, 4] else action

    # Reformat reward distribution settings
    if isinstance(payoff_dict, dict):
        setting = list()
        for i in range(2):
            # NOTE: the use of "set" discards the ordering of values in the
            # payoff distributions
            for out_i in list(set(payoff_dict[i])):
                prob_i = payoff_dict[i].count(out_i) / len(payoff_dict[i])
                setting.append(out_i)
                setting.append(prob_i)
    elif isinstance(payoff_dict, np.ndarray):
        setting = payoff_dict
    elif payoff_dict == 'n/a':
        setting = ['n/a'] * 8
    (mag0_1, prob0_1, mag0_2, prob0_2, mag1_1, prob1_1, mag1_2,
     prob1_2) = setting

    # turn byte into integer if we sent a trigger
    value = ord(value) if isinstance(value, bytes) else 'n/a'

    if onset != 'n/a':
        onset = onset - (deduct_onset_frames / fps)

    # Write the data
    with open(fpath, 'a') as fout:
        data = [onset,
                duration / fps,
                trial,
                action_type, action, outcome, response_time,
                value,
                mag0_1, prob0_1, mag0_2, prob0_2,
                mag1_1, prob1_1, mag1_2, prob1_2,
                version,
                int(reset),
                tr.get_system_time_stamp()]
        line = '\t'.join([str(i) for i in data])
        fout.write(line + '\n')


def get_fixation_stim(win, back_color=(0, 0, 0), stim_color=(1, 1, 1)):
    u"""Provide objects to represent a fixation stimulus as in [1]_.

    Parameters
    ----------
    win : psychopy.visual.Window
        The psychopy window on which to draw the fixation stimulus.
    back_color : tuple
        Color of the background (-1=black, 0=gray, 1=white)
    stim_color : tuple
        Color of the stimulus (-1=black, 0=gray, 1=white)

    Returns
    -------
    outer, inner, horz, vert : tuple of objects
        The objects that make up the fixation stimulus.

    References
    ----------
    .. [1] Thaler, L., Schütz, A. C., Goodale, M. A., & Gegenfurtner, K. R.
       (2013). What is the best fixation target? The effect of target shape on
       stability of fixational eye movements. Vision Research, 76, 31-42.
       https://www.doi.org/10.1016/j.visres.2012.10.012

    """
    # Lazy import to not have Travis CI issues with psychopy
    from psychopy import visual

    # diameter outer circle = 0.6 degrees
    # diameter circle = 0.2 degrees
    outer = visual.Circle(win=win,
                          radius=0.6/2,
                          edges=32,
                          units='deg',
                          fillColor=stim_color,
                          lineColor=back_color)

    inner = visual.Circle(win=win,
                          radius=0.2/2,
                          edges=32,
                          units='deg',
                          fillColor=stim_color,
                          lineColor=stim_color)

    horz = visual.Rect(win=win,
                       units='deg',
                       width=0.6,
                       height=0.2,
                       fillColor=back_color,
                       lineColor=back_color)

    vert = visual.Rect(win=win,
                       units='deg',
                       width=0.2,
                       height=0.6,
                       fillColor=back_color,
                       lineColor=back_color)

    return(outer, inner, horz, vert)


def set_fixstim_color(stim, color):
    """Set the fill and line color of a stim."""
    stim.setFillColor(color)
    stim.setLineColor(color)
    return stim
