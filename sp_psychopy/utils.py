"""Provide utility functions for the main experiment.

main file: sp.py

"""
import numpy as np
from psychopy import visual

import sp_psychopy
from sp_psychopy.define_payoff_settings import get_random_payoff_dict

# Frames per second. Change depending on your hardware.
utils_fps = 60


class Fake_serial():
    """Convenience class to run the code without true serial connection."""

    def write(self, byte):
        """Take a byte and do nothing."""
        pass


def get_payoff(df, omniscent=False):
    """Go through df and calculate earnings of participant.

    Parameters
    ----------
    df : pandas.DataFrame
        Data that was collected in this block

    omniscent : bool
        Whether or not to simulate the earnings of an omniscent participant
        instead

    Returns
    -------
    payoff : int
        payoff in this df

    """
    ntrials = int(df['trial'].max()+1)
    outcomes = np.zeros(ntrials)
    for trial in range(ntrials):

        if omniscent:
            payoff_dict = get_passive_payoff_dict(df, trial)
            # For the present setting, calculate expected values for each of
            # the options
            evs = list()
            for option, distr in payoff_dict.items():
                ev_list = [i*(distr.count(i)/len(distr)) for i in set(distr)]
                evs.append(np.array(ev_list).sum())
            # The omniscent player picks a random draw from the objectively
            # better option
            outcome = np.random.choice(payoff_dict[evs.index(max(evs))])
        else:
            tmp_df = df[df['trial'] == trial]
            # The last outcome recorded in a trial is final choice outcome
            outcome = tmp_df['outcome'].dropna().tolist()[-1]

        outcomes[trial] = outcome
    # The payoff is the sum of outcomes
    payoff = int(np.sum(outcomes))
    return payoff


def get_passive_payoff_dict(df, trial):
    """Get data for a replay.

    Parameters
    ----------
    df : pandas.DataFrame
        Data to be replayed

    trial : int
        Indices into the data for which to fetch actions

    Returns
    -------
    payoff_dict : dict
        Dictionary containing the reward distribution setting of the current
        trial. NOTE: returns the "final" payoff_dict that was used for
        drawing the reward

    """
    # get the setting and reformat it to fit with internal usage in
    # `define_payoff_settings.py`
    # NOTE: always take the last available setting, because the previous ones
    #       (if there are any) have been dropped due to an error (if there was
    #       one)
    tmp_df = df[(df['trial'] == trial)]
    tmp_df = tmp_df.loc[:,  'mag0_1':'prob1_2'].dropna()
    wrong_format_setting = tmp_df.iloc[-1].tolist()
    setting = np.array(wrong_format_setting)[[0, 2, 1, 3, 4, 6, 5, 7]]
    setting = np.expand_dims(setting, 0)
    # quick sanity check that we have proper roundings, for example 0.3 instead
    # of 0.29999999 ... 1., 2., 3., etc. would be fine (as magnitudes)
    for entry in setting[0]:
        assert len(str(entry)) in [2, 3]  # 2 for magnitudes, 3 for probs
    payoff_dict, payoff_settings = get_random_payoff_dict(setting)
    return payoff_dict


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
    key = {0: 'left', 1: 'right', 2: 'down'}[key]
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


def get_jittered_waitframes(min_wait, max_wait, fps=utils_fps):
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


def log_data(fpath, onset='n/a', duration=0, trial='n/a', action='n/a',
             outcome='n/a', response_time='n/a', value='n/a',
             payoff_dict='n/a', fps=utils_fps, version=sp_psychopy.__version__,
             reset=False):
    """Write data to the log file.

    All inputs except the file path default to 'n/a'.

    See also the 'task-sp_events.json' file.

    Parameters
    ----------
    fpath : str
        Path to the log file.

    onset : float | 'n/a'
        onset of the event in seconds

    duration : int | 0
        duration of the event in frames. Will then be converted to seconds by
        dividing with `utils_fps`.

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

    payoff_dict : dict | 'n/a'
        Dictionary containing the reward distribution setting of the current
        trial.

    fps : int
        frames per second used in this experiment

    version : str
        version of the experiment used for collecting this data

    reset : bool
        if True, discard all prior events in the current trial because of
        an error of the participant. If False, ignore it

    """
    # Infer action type
    action_type_dict = dict()
    action_type_dict[0] = 'sample'
    action_type_dict[1] = 'sample'
    action_type_dict[2] = 'stop'
    action_type_dict[3] = 'final_choice'
    action_type_dict[4] = 'final_choice'
    action_type_dict[5] = 'forced_stop'
    action_type_dict[6] = 'forced_stop'
    action_type_dict[7] = 'premature_stop'
    action_type_dict['n/a'] = 'n/a'

    action_type = action_type_dict[action]
    if action in [5, 6]:
        action = action - 5
    elif action == 7:
        action = 2
    elif action != 'n/a':
        action = (action - 3) if action in [3, 4] else action

    # Reformat reward distribution settings
    if payoff_dict != 'n/a':
        assert len(payoff_dict) == 2
        setting = list()
        for i in range(2):
            for out_i in list(set(payoff_dict[i])):
                prob_i = payoff_dict[i].count(out_i) / len(payoff_dict[i])
                setting.append(out_i)
                setting.append(prob_i)
    else:
        setting = ['n/a'] * 8
    (mag0_1, prob0_1, mag0_2, prob0_2, mag1_1, prob1_1, mag1_2,
     prob1_2) = setting

    # turn byte into integer if we sent a trigger
    value = ord(value) if isinstance(value, bytes) else 'n/a'

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
                int(reset)]
        line = '\t'.join([str(i) for i in data])
        fout.write(line + '\n')


def set_fixstim_color(stim, color):
    """Set the fill and line color of a stim."""
    stim.setFillColor(color)
    stim.setLineColor(color)
    return stim


def get_fixation_stim(win):
    u"""Provide objects to represent a fixation stimulus as in [1].

    Parameters
    ----------
    win : psychopy.visual.Window
        The psychopy window on which to draw the fixation stimulus.

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
    # diameter outer circle = 0.6 degrees
    # diameter circle = 0.2 degrees
    outer = visual.Circle(win=win,
                          radius=0.6/2,
                          edges=32,
                          units='deg',
                          fillColor=[1., 1., 1.],
                          lineColor=[0., 0., 0.])

    inner = visual.Circle(win=win,
                          radius=0.2/2,
                          edges=32,
                          units='deg',
                          fillColor=[1., 1., 1.],
                          lineColor=[1., 1., 1.])

    horz = visual.Line = visual.Rect(win=win,
                                     units='deg',
                                     width=0.6,
                                     height=0.2,
                                     fillColor=[0., 0., 0.],
                                     lineColor=[0., 0., 0.])

    vert = visual.Line = visual.Rect(win=win,
                                     units='deg',
                                     width=0.2,
                                     height=0.6,
                                     fillColor=[0., 0., 0.],
                                     lineColor=[0., 0., 0.])

    return(outer, inner, horz, vert)
