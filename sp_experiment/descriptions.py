"""Inquire participant's decisions from descriptions.

Based on a data file collected in the active SP condition, provide gambles
from descriptions.

Notes
-----
When we display the description task according to *experienced* data, it might
happen that during the experienced condition (i) a distribution was not sampled
or (ii) not all outcomes were encountered while sampling a distribution. We
deal with this as such:

(i) we simply display all probabilities as if they were from the true condition
    (i.e., the true underlying probabilities) ... then we can later drop that
    trial from the data before analysis. This will not disrupt the paradigm
    flow ... and it's an event that is expected to happen very rarely
(ii) we show only the outcomes that WERE encountered, and if they were the
     only ones for a distribution, we assign them the probability of 1

"""
import os.path as op
import warnings

import pandas as pd
import numpy as np
from psychopy import visual, event, core, monitors
import tobii_research as tr

from sp_experiment.define_ttl_triggers import provide_trigger_dict
from sp_experiment.define_payoff_settings import get_payoff_dict
from sp_experiment.define_variable_meanings import make_description_task_json
from sp_experiment.define_instructions import (provide_start_str,
                                               provide_stop_str,
                                               provide_blockfbk_str
                                               )
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
                                           color_magnitude,
                                           color_probability,
                                           tdisplay_ms,
                                           tfeeddelay_ms,
                                           toutmask_ms,
                                           toutshow_ms,
                                           fraction_to_run
                                           )


def run_descriptions(events_file, monitor='testMonitor', ser=Fake_serial(),
                     block_size=1, font='', lang='de', experienced=False,
                     is_test=False, xpos1=2.5, xpos2=1.5,
                     colmag=color_magnitude, colprob=color_probability,
                     height=1, fraction_to_run=fraction_to_run,
                     quit_after_n=None):
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
    block_size : int
        Number of trials after which feedback is provided
    experienced : bool
        Whether to base lotteries on experienced distributions.
    xpos1, xpos2 : float
        X-axis positions of the two Text stimuli that make up one lottery.
        The difference between xpos1 and xpos2 determines the space between
        the displayed magnitude and associated probability
    colmag, colprob: tuple
        Color tuples of how to display magnitude text and probability text
    height: int
        Height of the text stimuli
    fraction_to_run : float
        Fraction of all trials to run. Must be > 0 and <= 1. If smaller than 1,
        will make a random selection of trials to run.
    quit_after_n : None | int
        Has no impact if None. If int, determines the number of trials to
        run before quitting

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

    # How many trials can we present at most?
    ntrials = int(df['trial'].max())+1

    # In case we only want a subset of all possible trials in description
    if fraction_to_run == 1:
        trials_to_run = list(range(ntrials))
    elif fraction_to_run <= 0 or fraction_to_run > 1:
        raise ValueError('fraction_to_run must be > 0 and <=1 but is {}'
                         .format(fraction_to_run))
    else:
        # fraction is > 0 but < 1
        rand_selection = np.random.permutation(ntrials)
        count = int(np.ceil(ntrials * fraction_to_run))
        trials_to_run_arr = rand_selection[:count]
        trials_to_run = sorted(trials_to_run_arr)

    # Maker sure our number of trials fits with number of blocks
    no_match_blocks_trials = False
    if quit_after_n:
        nblocks = int(quit_after_n/block_size)
        if quit_after_n % block_size != 0:
            no_match_blocks_trials = True
    else:
        nblocks = int(len(trials_to_run)/block_size)
        if len(trials_to_run) % block_size != 0:
            no_match_blocks_trials = True

    # If we found that blocks and trials don't match, raise an error
    if no_match_blocks_trials:
        raise ValueError('block_size of {} and trials_to_run of len {} '
                         'do not match.\n\nTrials to run: {}'
                         .format(block_size, len(trials_to_run),
                                 trials_to_run))

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
        # However, the initial state should be 0.5 (center according to tobii
        # coordinate system)
        assert gaze_dict['gaze'][0][0] == 0.5
        assert gaze_dict['gaze'][1][0] == 0.5
        gaze_data_callback = get_gaze_data_callback(eyetrack_fpath)
        eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback,
                                as_dictionary=True)
        # Collect for a bit and confirm that we truly get the gaze data
        core.wait(1)
        assert gaze_dict['gaze'][0][0] != 0.5
        assert gaze_dict['gaze'][1][0] != 0.5
        assert op.exists(eyetrack_fpath)

    # Trigger meanings and values
    trig_dict = provide_trigger_dict()

    # Define monitor specific window object
    my_monitor = monitors.Monitor(name=monitor)
    win = visual.Window(color=(0, 0, 0),  # Background color: RGB [-1,1]
                        fullscr=True,  # Fullscreen for better timing
                        monitor=my_monitor,
                        winType='pyglet',
                        size=my_monitor.getSizePix())

    # Hide the cursor
    win.mouseVisible = False

    # On which frame rate are we operating? Try getting it several times
    # because it can fluctuate a bit
    fps_counter = 0
    while True:
        fps = win.getActualFrameRate(nMaxFrames=1000)
        if fps is not None:
            fps = int(round(fps))
            print('found fps: {}'.format(fps))
        if EXPECTED_FPS == fps:
            break
        else:
            fps_counter += 1
            core.wait(1)
        if fps_counter > 3:
            raise ValueError('Please adjust the EXPECTED_FPS variable '
                             'in define_settings.py')

    # prepare text objects
    txt_stim = visual.TextStim(win, color=txt_color, units='deg', pos=(0, 0),
                               height=1, font=font)

    txt_left1 = visual.TextStim(win, color=colmag, units='deg',
                                pos=(-xpos1, 0), height=height, font=font)
    txt_left2 = visual.TextStim(win, color=colprob, units='deg',
                                pos=(-xpos2, 0), height=height, font=font)

    txt_right1 = visual.TextStim(win, color=colmag, units='deg',
                                 pos=(xpos2, 0), height=height, font=font)
    txt_right2 = visual.TextStim(win, color=colprob, units='deg',
                                 pos=(xpos1, 0), height=height, font=font)

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

    # Get ready to start the experiment. Start timing from next button press.
    txt_stim.text = provide_start_str(is_test=is_test, condition='description',
                                      lang=lang)
    txt_stim.draw()
    win.flip()
    event.waitKeys()
    value = trig_dict['trig_begin_experiment']
    ser.write(value)
    exp_timer = core.MonotonicClock()
    log_data(data_file, onset=exp_timer.getTime(),
             value=value)
    txt_stim.height = 4  # set height for stimuli to be shown below

    # Now collect the data
    current_nblocks = 0
    for trial in trials_to_run:

        # Prepare lotteries for a new trial
        # Extract the true magnitudes and probabilities
        setting = _get_payoff_setting(df, trial)
        payoff_dict = get_payoff_dict(setting)
        setting[0, [2, 3, 6, 7]] *= 100  # multiply probs to be in percent
        setting = setting.astype(int)

        # Magnitudes are always set
        mag0_1 = setting[0, 0]
        mag0_2 = setting[0, 1]
        mag1_1 = setting[0, 4]
        mag1_2 = setting[0, 5]

        # Setting of probabilities depends on argument `experienced`
        if experienced:
            # Get experienced probabilities (magnitudes are the same ... or
            # will be added if never experienced - either with p=0 and other
            # *experienced* outcome p=1 ... or both with p=0.5 if both of the
            # outcomes have not been experienced)
            exp_setting = _get_payoff_setting(df, trial, experienced)
            exp_setting[0, [2, 3, 6, 7]] *= 100  # multiply probs to percent
            exp_setting = exp_setting.astype(int)

            prob0_1 = exp_setting[0, 2]
            prob0_2 = exp_setting[0, 3]
            prob1_1 = exp_setting[0, 6]
            prob1_2 = exp_setting[0, 7]

            # Need to make sure it always sums to 100
            def _adjust_to_100(p1, p2, trial):
                """If p1 and p2 do not sum to 100, adjust them."""
                # We might encounter special values 98 and 99 ... in that case
                # ignore any issues and just proceed. These will be replaced
                # later.
                suppress_warning = False
                if p1 in [9800, 9900] or p2 in [9800, 9900]:  # were *100 above
                    suppress_warning = True

                if p1 + p2 != 100:
                    cointoss = np.random.choice([0, 1])
                    if cointoss == 0:
                        p1 = 100 - p2
                    else:
                        p2 = 100 - p1
                try:
                    assert p1 + p2 == 100
                    assert p1 >= 0 and p1 <= 100
                    assert p2 >= 0 and p2 <= 100
                except AssertionError:
                    if not suppress_warning:
                        warnings.warn('Probabilities do not add to 100. '
                                      'Trial:{}, p1={}, p2={}'
                                      .format(trial, p1, p2))
                return p1, p2

            prob0_1, prob0_2 = _adjust_to_100(prob0_1, prob0_2, trial)
            prob1_1, prob1_2 = _adjust_to_100(prob1_1, prob1_2, trial)

            # If a distribution has not been sampled, display standard probs
            # we can drop the trial from analysis
            if 99 in exp_setting:
                prob0_1 = setting[0, 2]
                prob0_2 = setting[0, 3]
                prob1_1 = setting[0, 6]
                prob1_2 = setting[0, 7]

            # Else, if not all 4 outcomes were observed, adjust probabilities
            # to simulate "safe" lotteries
            elif 98 in exp_setting:
                if exp_setting[0, 0] == 98:
                    mag0_1 = np.nan
                    prob0_1 = np.nan
                    prob0_2 = 100
                if exp_setting[0, 1] == 98:
                    mag0_2 = np.nan
                    prob0_2 = np.nan
                    prob0_1 = 100
                if exp_setting[0, 4] == 98:
                    mag1_1 = np.nan
                    prob1_1 = np.nan
                    prob1_2 = 100
                if exp_setting[0, 5] == 98:
                    mag1_2 = np.nan
                    prob1_2 = np.nan
                    prob1_1 = 100

        # If not running in experienced mode ...
        else:
            # Use true probabilities
            prob0_1 = setting[0, 2]
            prob0_2 = setting[0, 3]
            prob1_1 = setting[0, 6]
            prob1_2 = setting[0, 7]

        # log used setting and convert back probabilities back to proportions
        used_setting = np.asarray([mag0_1, np.round(prob0_1/100, 2),
                                   mag0_2, np.round(prob0_2/100, 2),
                                   mag1_1, np.round(prob1_1/100, 2),
                                   mag1_2, np.round(prob1_2/100, 2)])
        log_data(data_file, onset=exp_timer.getTime(), trial=trial,
                 payoff_dict=used_setting)

        # Start new trial
        for stim in fixation_stim_parts:
            stim.setAutoDraw(True)
        set_fixstim_color(inner, color_newtrl)
        value = trig_dict['trig_new_trl']
        win.callOnFlip(ser.write, value)
        frames = get_jittered_waitframes(*tdisplay_ms)
        for frame in range(frames):
            win.flip()
            if frame == 1:
                log_data(data_file, onset=exp_timer.getTime(),
                         trial=trial, value=value, duration=frames,
                         deduct_onset_frames=1)

        # Present lotteries
        # make not encountered magnitudes an empty string so they don't show
        mag0_1 = mag0_1 if not np.isnan(mag0_1) else ''
        mag0_2 = mag0_2 if not np.isnan(mag0_2) else ''
        mag1_1 = mag1_1 if not np.isnan(mag1_1) else ''
        mag1_2 = mag1_2 if not np.isnan(mag1_2) else ''

        # make probs of not-encountered magnitudes an empty string as well
        prob0_1 = str(prob0_1) if not np.isnan(prob0_1) else ''
        prob0_2 = str(prob0_2) if not np.isnan(prob0_2) else ''
        prob1_1 = str(prob1_1) if not np.isnan(prob1_1) else ''
        prob1_2 = str(prob1_2) if not np.isnan(prob1_2) else ''

        txt_left1.text = '{}\n{}'.format(mag0_1, mag0_2)
        txt_left2.text = '{}\n{}'.format(prob0_1, prob0_2)

        txt_right1.text = '{}\n{}'.format(mag1_1, mag1_2)
        txt_right2.text = '{}\n{}'.format(prob1_1, prob1_2)

        set_fixstim_color(inner, color_standard)
        txt_left1.draw()
        txt_left2.draw()
        txt_right1.draw()
        txt_right2.draw()
        value = trig_dict['trig_final_choice_onset']
        win.callOnFlip(ser.write, value)
        rt_clock.reset()
        log_data(data_file, onset=exp_timer.getTime(), trial=trial,
                 value=value)
        win.flip()

        # Collect response
        keys_rts = event.waitKeys(maxWait=float('inf'),
                                  keyList=KEYLIST_DESCRIPTION,
                                  timeStamped=rt_clock)
        key, rt = keys_rts[0]
        action = KEYLIST_DESCRIPTION.index(key)

        if action == 0:
            value = trig_dict['trig_left_final_choice']
            trig_val_mask = trig_dict['trig_mask_final_out_l']
            trig_val_show = trig_dict['trig_show_final_out_l']
            pos = (-5, 0)
        elif action == 1:
            value = trig_dict['trig_right_final_choice']
            trig_val_mask = trig_dict['trig_mask_final_out_r']
            trig_val_show = trig_dict['trig_show_final_out_r']
            pos = (5, 0)
        elif action == 2:
            win.close()
            core.quit()

        ser.write(value)
        # increment action by 3 to log a final choice instead of a "sample"
        log_data(data_file, onset=exp_timer.getTime(), trial=trial,
                 action=action+3, response_time=rt, value=value)
        # Draw outcome
        # First need to re-engineer our payoff_dict with the actually used
        # setting
        wrong_format_used_setting = used_setting[[0, 2, 1, 3, 4, 6, 5, 7]]
        wrong_format_used_setting = np.expand_dims(wrong_format_used_setting,
                                                   0)
        payoff_dict = get_payoff_dict(wrong_format_used_setting)
        outcome = np.random.choice(payoff_dict[action])

        # Prepare feedback
        circ_stim.pos = pos
        txt_stim.pos = pos
        txt_stim.text = str(outcome)
        # manually push text to center of circle
        txt_stim.pos += (0, 0.3)
        txt_stim.color = (0, 1, 0)  # make green, because it is consequential

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
            if frame == 1:
                log_data(data_file, onset=exp_timer.getTime(), trial=trial,
                         duration=frames, value=trig_val_mask,
                         deduct_onset_frames=1)

        win.callOnFlip(ser.write, trig_val_show)
        frames = get_jittered_waitframes(*toutshow_ms)
        for frame in range(frames):
            circ_stim.draw()
            txt_stim.draw()
            win.flip()
            if frame == 1:
                log_data(data_file, onset=exp_timer.getTime(), trial=trial,
                         duration=frames, outcome=outcome, value=trig_val_show,
                         deduct_onset_frames=1)

        # reset text color
        txt_stim.color = color_standard

        # Is a block finished? If yes, display block feedback and
        # provide a short break
        nth_trial = trials_to_run.index(trial) + 1
        if nth_trial % block_size == 0:
            current_nblocks += 1
            for stim in fixation_stim_parts:
                stim.setAutoDraw(False)
            txt_stim.text = provide_blockfbk_str(data_file,
                                                 current_nblocks,
                                                 nblocks,
                                                 lang=lang)
            txt_stim.pos = (0, 0)
            txt_stim.height = 1
            txt_stim.draw()
            value = trig_dict['trig_block_feedback']
            win.callOnFlip(ser.write, value)
            win.flip()
            log_data(data_file, onset=exp_timer.getTime(), value=value)
            core.wait(1)  # wait for a bit so that this is not skipped
            event.waitKeys()

            # Reset stim settings for next block
            for stim in fixation_stim_parts:
                stim.setAutoDraw(True)
            # set height for stimuli to be shown below
            txt_stim.height = 4

        # If quit_after_n is defined, we might need to stop here
        if quit_after_n:
            if nth_trial >= quit_after_n:
                break

    # We are done here
    for stim in fixation_stim_parts:
        stim.setAutoDraw(False)
    txt_stim.text = provide_stop_str(is_test=is_test, lang=lang)
    txt_stim.pos = (0, 0)
    txt_stim.height = 1
    txt_stim.draw()
    value = trig_dict['trig_end_experiment']
    win.callOnFlip(ser.write, value)
    win.flip()
    log_data(data_file, onset=exp_timer.getTime(), value=value)
    event.waitKeys()

    # Stop recording eye data and reset gaze to default
    if track_eyes:
        eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA,
                                    gaze_data_callback)
    gaze_dict['gaze'] = ((0.5, 0.5), (0.5, 0.5))
    win.close()
