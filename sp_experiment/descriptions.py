"""Inquire participant's decisions from descriptions.

Based on a data file collected in the active SP condition, provide gambles
from descriptions.
"""
import os
import os.path as op

import pandas as pd
import numpy as np
from psychopy import visual, event, core
import tobii_research as tr

import sp_experiment
from sp_experiment.define_ttl_triggers import provide_trigger_dict
from sp_experiment.define_payoff_settings import get_random_payoff_dict
from sp_experiment.define_variable_meanings import make_description_task_json
from sp_experiment.define_instructions import instruct_str_descriptions
from sp_experiment.utils import (_get_payoff_setting,
                                 get_fixation_stim,
                                 set_fixstim_color,
                                 Fake_serial,
                                 get_jittered_waitframes,
                                 log_data)
from sp_experiment.define_eyetracker import (find_eyetracker,
                                             get_gaze_data_callback,
                                             gaze_dict,
                                             )
from sp_experiment.define_settings import (KEYLIST_DESCRIPTION,
                                           EXPECTED_FPS,
                                           txt_color,
                                           circ_color,
                                           color_newtrl,
                                           color_standard,
                                           ser,
                                           tdisplay_ms,
                                           tfeeddelay_ms,
                                           toutmask_ms,
                                           toutshow_ms
                                           )


def run_descriptions(events_file, monitor='testMonitor', ser=Fake_serial(),
                     font='', lang='de', experienced=False):
    """Run decisions from descriptions.

    Parameters
    ----------
    events_file : str
        Path to sub-{id:02d}_task-spactive_events.tsv file for
        a given subject id.
    monitor : str
        Monitor definitionto be used, see define_monitors.py
    ser : str | instance of Fake_serial. Defaults to None.
        Either string address to a serial port for sending triggers, or
        a Fake_serial object, see utils.py. Defaults to Fake_serial.
    experienced : bool
        Whether to base lotteries on true or on experienced distributions.

    Returns
    -------
    data_file : str
        Path to the output data file

    """
    # prepare logging and read in present data
    df = pd.read_csv(events_file, sep='\t')
    head, tail = op.split(events_file)
    sub_part = tail.split('_task')[0]
    fname = sub_part + '_task-description_events.tsv'
    data_file = op.join(head, fname)

    variable_meanings_dict = make_description_task_json()
    variables = list(variable_meanings_dict.keys())
    with open(data_file, 'w') as fout:
        header = '\t'.join(variables)
        fout.write(header + '\n')

    # Prepare eyetracking
    try:
        eyetracker = find_eyetracker()
        track_eyes = True
    except RuntimeError:
        print('Not using eyetracking. Did not find a tracker')
        track_eyes = False

    if track_eyes:
        print('Using eyetracker. Starting data collection now.')
        head, tail = op.split(data_file)
        if 'events' in tail:
            eyetrack_fname = tail.replace('events', 'eyetracking')
        else:
            eyetrack_fname = 'eyetracking' + tail
        eyetrack_fpath = op.join(head, eyetrack_fname)
        # This callback and the subscription method call will regularly
        # update the gaze_dict['gaze'] tuple with the left and right gaze point
        # However, the initial state should be 0
        assert gaze_dict['gaze'][0][0] == 0
        assert gaze_dict['gaze'][1][0] == 0
        gaze_data_callback = get_gaze_data_callback(eyetrack_fpath)
        eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback,
                                as_dictionary=True)
        # Collect for a bit and confirm that we truly get the gaze data
        core.wait(1)
        assert gaze_dict['gaze'][0][0] != 0
        assert gaze_dict['gaze'][1][0] != 0
        assert op.exists(eyetrack_fpath)

    # Trigger meanings and values
    trig_dict = provide_trigger_dict()

    # Define monitor specific window object
    win = visual.Window(color=(0, 0, 0),  # Background color: RGB [-1,1]
                        fullscr=True,  # Fullscreen for better timing
                        monitor=monitor,
                        winType='pyglet')

    # Hide the cursor
    win.mouseVisible = False

    # On which frame rate are we operating?
    fps = int(round(win.getActualFrameRate()))
    if EXPECTED_FPS != fps:
        raise ValueError('Please adjust the EXPECTED_FPS variable '
                         'in define_settings.py')

    # prepare text objects
    txt_stim = visual.TextStim(win,
                               color=txt_color,
                               units='deg',
                               pos=(0, 0))
    txt_stim.height = 1
    txt_stim.font = font

    txt_left = visual.TextStim(win,
                               color=txt_color,
                               units='deg',
                               pos=(-2, 0))
    txt_left.height = 1
    txt_left.font = font

    txt_right = visual.TextStim(win,
                                color=txt_color,
                                units='deg',
                                pos=(2, 0))
    txt_right.height = 1
    txt_right.font = font

    # Prepare circle stim for presenting outcomes
    circ_stim = visual.Circle(win,
                              pos=(0, 0),
                              units='deg',
                              fillColor=circ_color,
                              lineColor=circ_color,
                              radius=2.5,
                              edges=128)

    # Get the objects for the fixation stim
    outer, inner, horz, vert = get_fixation_stim(win, stim_color=txt_color)
    fixation_stim_parts = [outer, horz, vert, inner]

    # Start a clock for measuring reaction times
    # NOTE: Will be reset to 0 right before recording a button press
    rt_clock = core.Clock()

    # Start a clock for general experiment time
    exp_timer = core.MonotonicClock()

    # Print some instructions
    txt_stim.text = instruct_str_descriptions(lang)
    txt_stim.draw()
    win.flip()
    event.waitKeys()

    # set height for stimuli to be shown below
    txt_stim.height = 4

    # Now collect the data
    ntrials = int(df['trial'].max())+1
    for trial in range(ntrials+10):  # XXX
        trial = 0  # XXX
        # Start new trial
        [stim.setAutoDraw(True) for stim in fixation_stim_parts]
        set_fixstim_color(inner, color_newtrl)
        win.callOnFlip(ser.write, trig_dict['trig_new_trl'])
        frames = get_jittered_waitframes(*tdisplay_ms)
        for frame in range(frames):
            win.flip()

        # Prepare lotteries
        # Extract the true magnitudes and probabilities
        setting = _get_payoff_setting(df, trial)
        payoff_dict, __ = get_random_payoff_dict(setting)
        setting[0, [2, 3, 6, 7]] *= 100  # multiply probs to be in percent
        setting = setting.astype(int)

        # Magnitudes are always set
        mag0_1 = setting[0, 0]
        mag0_2 = setting[0, 1]
        mag1_1 = setting[0, 4]
        mag1_2 = setting[0, 5]

        # Setting of probabilities depends on argument `experienced`
        if experienced:
            # Get experienced probabilities (magnitudes are the same)
            exp_setting = _get_payoff_setting(df, trial, experienced)
            exp_setting[0, [2, 3, 6, 7]] *= 100  # multiply probs to percent
            exp_setting = exp_setting.astype(int)

            prob0_1 = exp_setting[0, 2]
            prob0_2 = exp_setting[0, 3]
            prob1_1 = exp_setting[0, 6]
            prob1_2 = exp_setting[0, 7]
        else:
            # Use true probabilities
            prob0_1 = setting[0, 2]
            prob0_2 = setting[0, 3]
            prob1_1 = setting[0, 6]
            prob1_2 = setting[0, 7]

        # Present lotteries
        txt_left.text = '{}|{}\n{}|{}'.format(mag0_1, prob0_1,
                                              mag0_2, prob0_2)
        txt_right.text = '{}|{}\n{}|{}'.format(mag1_1, prob1_1,
                                               mag1_2, prob1_2)

        set_fixstim_color(inner, color_standard)
        txt_left.draw()
        txt_right.draw()
        rt_clock.reset()
        onset = exp_timer.getTime()
        win.flip()
        # Collect response
        keys_rts = event.waitKeys(maxWait=float('inf'),
                                  keyList=KEYLIST_DESCRIPTION,
                                  timeStamped=rt_clock)
        key, rt = keys_rts[0]
        action = KEYLIST_DESCRIPTION.index(key)

        if action == 0:
            value = trig_dict['trig_left_choice']
            trig_val_mask = trig_dict['trig_mask_out_l']
            trig_val_show = trig_dict['trig_show_out_l']
            pos = (-5, 0)
        elif action == 1:
            value = trig_dict['trig_right_choice']
            trig_val_mask = trig_dict['trig_mask_out_r']
            trig_val_show = trig_dict['trig_show_out_r']
            pos = (5, 0)
        elif action == 2:
            win.close()
            core.quit()

        ser.write(value)

        # Draw outcome
        outcome = np.random.choice(payoff_dict[action])

        # Prepare feedback
        circ_stim.pos = pos
        txt_stim.pos = pos
        txt_stim.text = str(outcome)
        # manually push text to center of circle
        txt_stim.pos += (0, 0.3)

        # delay feedback
        frames = get_jittered_waitframes(*tfeeddelay_ms)
        for frame in range(frames):
            win.flip()

        # Show feedback
        win.callOnFlip(ser.write, trig_val_mask)
        frames = get_jittered_waitframes(*toutmask_ms)
        for frame in range(frames):
            circ_stim.draw()
            win.flip()
            if frame == 0:
                log_data(data_file, onset=exp_timer.getTime(),
                         trial=trial, duration=frames,
                         value=trig_val_mask)

        win.callOnFlip(ser.write, trig_val_show)
        frames = get_jittered_waitframes(*toutshow_ms)
        for frame in range(frames):
            circ_stim.draw()
            txt_stim.draw()
            win.flip()
            if frame == 0:
                log_data(data_file, onset=exp_timer.getTime(),
                         trial=trial, duration=frames,
                         outcome=outcome,
                         value=trig_val_show)

        # Log the data
        with open(data_file, 'a') as fout:
            values = [onset, rt, trial, action]
            values = [str(val) for val in values]
            fout.write('\t'.join(values))

    return data_file


if __name__ == '__main__':
    # Check serial
    if ser is None:
        ser = Fake_serial()

    init_dir = op.dirname(sp_experiment.__file__)
    fname = 'sub-999_task-spactive_events.tsv'
    fpath = op.join(init_dir, 'tests', 'data', fname)
    data_file = run_descriptions(fpath, experienced=True)
    os.remove(data_file)
