"""Provide utility functions for the main experiment.

main file: sp.py

"""
from psychopy import visual, event, core
from numpy import random


def inquire_action(win, ser, timeout_seconds,
                   keylist=['left', 'right', 'down', 'x'],
                   trig_left=None,
                   trig_right=None,
                   trig_final=None):
    """Wait for an action and send a TTL trigger once it happened.

    Parameters
    ----------
    win : psychopy.visual.Window
        The psychopy window on which to draw the outcome.

    ser : serial.Serial
        The port over which to send a trigger

    timeout_seconds : float | 'inf'
        Maximum number of seconds to wait for an action. Or 'inf' to wait
        forever.

    keylist : list
        The list of keys that are valid responses. Practically, this should
        be used to pass a reduced list ['left', 'right'] as parameter for
        "final choices", when only one of two options can be selected.

    trig_left_choice, trig_right_choice, trig_final_choice : byte
        Triggers to be sent at onset.

    Returns
    -------
    action : int, one of [0, 1, 2]
        The selected action. [0, 1] refer to sampling one or the other option,
        2 refers to stopping to sample and making a final choice.

    rt : float
        The reaction time in seconds.

    Notes
    -----
    Using event.waitKeys(), which will stop everything while waiting for a key
    press. According to [1] this has a better time resolution than
    event.getKeys().

    References
    ----------
    .. [1] https://groups.google.com/forum/#!topic/psychopy-dev/u3WyDfnIYBo

    """
    timer = core.Clock()
    keys = event.waitKeys(maxWait=timeout_seconds,
                          keyList=keylist,
                          timeStamped=timer)
    if keys:
        assert len(keys) == 1
        action, rt = keys[0]
        if action == 'left':
            ser.write(trig_left)
            action = 0
        elif action == 'right':
            ser.write(trig_right)
            action = 1
        elif action == 'down':
            ser.write(trig_final)
            action = 2
        else:  # action == 'x':
            win.close()
            core.quit()

        return action, abs(rt)

    # Timeout, trigger BAD TRIAL message shutdown
    else:
        print('TIMEOUT during inquire_action ... shutting down.')
        print('Consider not using a timeout by passing float("Inf")')
        win.close()
        core.quit()


def display_outcome(win, ser, action, payoff_dict, mask_frames, show_frames,
                    trig_mask=None, trig_show=None):
    """Display the outcome of an action.

    Parameters
    ----------
    win : psychopy.visual.Window
        The psychopy window on which to draw the outcome.

    ser : serial.Serial
        The port over which to send a trigger

    action : int, one of [0, 1]
        The selected action.

    payoff_dict : dict
        Dictionary with as many keys as there are actions. For each action key,
        there is an associated list of outcomes representing the payoff
        distribution for that action.

    mask_frames : int
        Number of frames to mask the outcome

    show_frames : int
        Number of frames to display the outcome

    trig_mask : byte
        Byte to send at onset of masking.

    trig_show : byte
        Byte to send at onset of outcome.

    Returns
    -------
    outcome : int
        The outcome that was displayed.

    """
    # First, draw the outcome
    outcome = random.choice(payoff_dict[action])

    # Where should it be displayed
    pos = (-5.5, 0.) if action == 0 else (5.5, 0.)
    circ_stim = visual.Circle(win,
                              pos=pos,
                              units='deg',
                              fillColor=(-1., -1., -1.),
                              lineColor=(-1., -1., -1.),
                              radius=2.5,
                              edges=128)

    txt_stim = visual.TextStim(win,
                               text=str(outcome),
                               pos=pos,
                               units='deg',
                               height=5,
                               color=(1., 1., 1.))

    # Mask the outcome, send a trigger for the first flip
    win.callOnFlip(ser.write, trig_mask)
    for frame in range(mask_frames):
        txt_stim.draw()
        circ_stim.draw()
        win.flip()

    # Flip the mask ... show the outcome, send a trigger for the first flip
    win.callOnFlip(ser.write, trig_show)
    for frame in range(show_frames):
        circ_stim.draw()
        txt_stim.draw()
        win.flip()

    return outcome


def display_message(win, ser, message, frames, trig=None):
    """Draw a message to the center of the screen for a number of frames.

    Parameters
    ----------
    win : psychopy.visual.Window
        The psychopy window on which to draw the outcome.

    ser : serial.Serial
        The port over which to send a trigger

    message : str
        The message.

    frames : int
        Number of frames to show the message

    trig : bytes
        TTL trigger to send upon onset.

    """
    txt_stim = visual.TextStim(win, text=message, units='deg', height=1)
    win.callOnFlip(ser.write, trig)
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
