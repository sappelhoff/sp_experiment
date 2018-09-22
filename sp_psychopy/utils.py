"""Provide utility functions for the main experiment."""
from psychopy import visual
from numpy import random


def display_outcome(win, action, payoff_dict, frames):
    """Display the outcome of an action.

    Parameters
    ----------
    win : psychopy.visual.Window
        The psychopy window on which to draw the outcome.

    action : int, one of [0, 1]
        The selected action.

    payoff_dict : dict
        Dictionary with as many keys as there are actions. For each action key,
        there is an associated list of outcomes representing the payoff
        distribution for that action.

    frames : int
        Number of frames to display the outcome

    Returns
    -------
    outcome : int
        The outcome that was displayed.

    """
    # First, draw the outcome
    outcome = random.choice(payoff_dict[action])

    # Where should it be displayed
    pos = (-0.5, 0) if action == 0 else (0.5, 0)
    circ_stim = visual.Circle(win, pos=pos, units='deg',
                              fillColor=(-1, -1, -1),
                              lineColor=(-1, -1, -1),
                              radius=0.5,
                              edges=128)
    txt_stim = visual.TextStim(win, text=str(outcome), pos=pos, units='deg')

    for frame in range(frames):
        circ_stim.draw()
        txt_stim.draw()
        win.flip()

    return outcome


def display_message(win, message, frames):
    """Draw a message to the center of the screen for a number of frames."""
    txt_stim = visual.TextStim(win, text=message)
    for frame in range(frames):
        txt_stim.draw()
        win.flip()


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
                          fillColor=[1, 1, 1],
                          lineColor=[0, 0, 0])

    inner = visual.Circle(win=win,
                          radius=0.2/2,
                          edges=32,
                          units='deg',
                          fillColor=[1, 1, 1],
                          lineColor=[1, 1, 1])

    horz = visual.Line = visual.Rect(win=win,
                                     units='deg',
                                     width=0.6,
                                     height=0.2,
                                     fillColor=[0, 0, 0],
                                     lineColor=[0, 0, 0])

    vert = visual.Line = visual.Rect(win=win,
                                     units='deg',
                                     width=0.2,
                                     height=0.6,
                                     fillColor=[0, 0, 0],
                                     lineColor=[0, 0, 0])

    return(outer, inner, horz, vert)
