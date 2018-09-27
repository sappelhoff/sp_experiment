"""Provide utility functions for the main experiment.

main file: sp.py

"""
from psychopy import visual, event, core
from numpy import random

# Frames per second. Change depending on your hardware.
utils_fps = 60


def tw_jit(min_wait, max_wait):
    """From a uniform distribution, determine a waiting time within an interval.

    Parameters
    ----------
    min_wait, max_wait : float | int
        The minimum and maximum wait time in frames.

    Returns
    -------
    wait_time : int
        A wait time in frames in the interval [min_wait, max_wait]

    """
    low = int(round(min_wait))
    high = int(round(max_wait))
    wait_time = random.randint(low, high+1)
    return wait_time


def log_data(fpath, onset='n/a', duration=0, action='n/a', outcome='n/a',
             response_time='n/a', event_value='n/a', fps=utils_fps):
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

    action : int, one of [1, 2, 3] | 'n/a'
        the concrete action that the subject performed for the action type

    outcome : int | 'n/a'
        the outcome that the subject received for their action

    response_time : float | 'n/a'
        the time it took the subject to respond after the onset of the event

    event_value : byte | 'n/a'
        the TTL trigger value (=EEG marker value) associated with an event

    """
    action_type_dict = dict()
    action_type_dict[0] = 'sample'
    action_type_dict[1] = 'sample'
    action_type_dict[2] = 'stop'
    action_type_dict[3] = 'final_choice'
    action_type_dict[4] = 'final_choice'
    action_type_dict['n/a'] = 'n/a'

    action_type = action_type_dict[action]
    if action != 'n/a':
        action = (action - 3) if action >= 3 else action

    with open(fpath, 'a') as fout:
        data = [onset,
                duration / fps,
                action_type,
                action,
                outcome,
                response_time,
                ord(event_value)]
        line = '\t'.join([str(i) for i in data])
        fout.write(line + '\n')


def inquire_action(win, ser, logfile, timer, timeout, final,
                   keylist=['left', 'right', 'down', 'x'],
                   trig_left=bytes([0]),
                   trig_right=bytes([0]),
                   trig_final=bytes([0]),
                   ):
    """Wait for an action and send a TTL trigger once it happened.

    Parameters
    ----------
    win : psychopy.visual.Window
        The psychopy window on which to draw the outcome.

    ser : serial.Serial
        The port over which to send a trigger

    logfile : str
        The path to the log file.

    timer : psychopy.core.Clock
        The timer of the overall experiment time.

    final : bool
        Qualifier whether the action to be inquired will be for a final
        choice or not.

    timeout : float | 'inf'
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
    keys = event.waitKeys(maxWait=timeout,
                          keyList=keylist,
                          timeStamped=timer)
    if keys:
        assert len(keys) == 1
        action, rt = keys[0]
        if action == 'left':
            ser.write(trig_left)
            action = 0 if not final else 3
            trig = trig_left
        elif action == 'right':
            ser.write(trig_right)
            action = 1 if not final else 4
            trig = trig_right
        elif action == 'down':
            ser.write(trig_final)
            action = 2
            trig = trig_final
        else:  # action == 'x':
            win.close()
            core.quit()

        # Log the data
        log_data(logfile, onset=timer.getTime(),
                 action=action, response_time=abs(rt), event_value=trig)

        # If this was for a final choice, we need to remap
        if final:
            action = (action - 3) if action >= 3 else action

        return action, abs(rt)

    # Timeout, trigger BAD TRIAL message shutdown
    else:
        print('TIMEOUT during inquire_action ... shutting down.')
        print('Consider not using a timeout by passing float("Inf")')
        win.close()
        core.quit()


def display_outcome(win, ser, logfile, timer, action, payoff_dict, mask_frames,
                    show_frames, trig_mask=bytes([0]), trig_show=bytes([0])):
    """Display the outcome of an action.

    Parameters
    ----------
    win : psychopy.visual.Window
        The psychopy window on which to draw the outcome.

    ser : serial.Serial
        The port over which to send a trigger

    logfile : str
        The path to the log file.

    timer : psychopy.core.Clock
        The timer of the overall experiment time.

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
        if frame == 0:
            log_data(logfile, onset=timer.getTime(), duration=mask_frames,
                     event_value=trig_mask)

    # Flip the mask ... show the outcome, send a trigger for the first flip
    win.callOnFlip(ser.write, trig_show)
    for frame in range(show_frames):
        circ_stim.draw()
        txt_stim.draw()
        win.flip()
        if frame == 0:
            log_data(logfile, onset=timer.getTime(), duration=show_frames,
                     outcome=outcome, event_value=trig_show)

    return outcome


def display_message(win, ser, logfile, timer, message, frames,
                    trig=bytes([0])):
    """Draw a message to the center of the screen for a number of frames.

    Parameters
    ----------
    win : psychopy.visual.Window
        The psychopy window on which to draw the outcome.

    ser : serial.Serial
        The port over which to send a trigger

    logfile : str
        The path to the log file.

    timer : psychopy.core.Clock
        The timer of the overall experiment time.

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
        if frame == 0:
            log_data(logfile, onset=timer.getTime(), duration=frames,
                     event_value=trig)


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
