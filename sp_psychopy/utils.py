"""Provide utility functions for the main experiment.

main file: sp.py

"""
import os
import os.path as op

from psychopy import visual, event, core
import numpy as np
from numpy import random

import sp_psychopy

# Frames per second. Change depending on your hardware.
utils_fps = 60

# Define font to be used in this experiment
init_dir = op.dirname(sp_psychopy.__file__)
font = 'courier'
# If it is a special font, add the .ttf file to be on the path defined below
font_fpath = font + '.ttf'
font_path = op.join(os.sep.join(init_dir.split(os.sep)[:-1]), font_fpath)


class Fake_serial():
    """Convenience class to run the code without true serial connection."""

    def write(self, byte):
        """Take a byte and do nothing."""
        pass


def tw_jit(min_wait, max_wait, fps=utils_fps):
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
    wait_frames = random.randint(low, high+1)
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
        Dictionary containint the reward distribution setting of the current
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
