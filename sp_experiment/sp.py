"""Simplified experimental flow.

NOTE: For implementing fixed horizon SP:
1. make a branch off this project called "open-horizon"
2. "master" will be turned into "fixed-horizon"
3. For fixed horizon SP, simply "forbid" the "down" key, which would
   otherwise be used to trigger a final choice.
4. That means simplyfing the part where actions are checked

TODO:
- incorporate eye tracking (gaze-contingent fixation cross)
- pre-pilot-testing
"""
import os
import os.path as op
import argparse
import json

import numpy as np
import pandas as pd
from psychopy import visual, event, core

import sp_experiment
from sp_experiment.define_variable_meanings import make_events_json_dict
from sp_experiment.utils import (utils_fps,
                                 set_fixstim_color,
                                 get_jittered_waitframes,
                                 log_data,
                                 Fake_serial,
                                 get_payoff_dict,
                                 get_passive_action,
                                 get_passive_outcome,
                                 get_final_choice_outcomes
                                 )
from sp_experiment.psychopy_utils import get_fixation_stim
from sp_experiment.define_payoff_settings import (get_payoff_settings,
                                                  get_random_payoff_dict
                                                  )
from sp_experiment.define_ttl_triggers import provide_trigger_dict

# TTL triggers and variable meanings
# ==================================
trigger_dict = provide_trigger_dict()
variable_meanings_dict = make_events_json_dict()

# Participant information
# =======================
parser = argparse.ArgumentParser()
parser.add_argument('--sub_id', '-s', type=str, required=True,
                    help='The subject identifier. Preferably a number.')
parser.add_argument('--condition', '-c', type=str, required=True,
                    help='The task condition. "active" or "passive"')
parser.add_argument('--yoke_to', '-y', type=str, required=False,
                    help=('Which participant to yoke this current passive run '
                          'to. Ignored in "active" condition. '))
args = parser.parse_args()


# Data logging
# ============
fname = 'sub-{}_task-sp{}_events.tsv'.format(args.sub_id, args.condition)

# Check directory is present and file name not yet used
init_dir = op.dirname(sp_experiment.__file__)
data_dir = op.join(init_dir, 'experiment_data')
if not op.exists(data_dir):
    os.mkdir(data_dir)
    # Write a json of variable descriptions
    with open(op.join(data_dir, 'task-sp_events.json'), 'w') as fout:
        json.dump(obj=variable_meanings_dict, fp=fout,
                  sort_keys=False, indent=4)

data_file = op.join(data_dir, fname)
if op.exists(data_file):
    raise OSError('A data file for {} '
                  'already exists: {}'.format(args.sub_id, data_file))

# Write header to the tab separated log file
variables = list(variable_meanings_dict.keys())

with open(data_file, 'w') as fout:
    header = '\t'.join(variables)
    fout.write(header + '\n')


# Get PsychoPy stimuli ready
# ==========================
# Define monitor specific window object
win = visual.Window(color=(0, 0, 0),  # Background color: RGB [-1,1]
                    fullscr=True,  # Fullscreen for better timing
                    monitor='eizoforis',  # see monitor_definition.py
                    units='deg',
                    winType='pyglet')

# Hide the cursor
win.mouseVisible = False

# On which frame rate are we operating?
fps = int(round(win.getActualFrameRate()))
assert fps == 60
if utils_fps != fps:
    raise ValueError('Please adjust the utils_fps variable in utils.py')

# Get the objects for the fixation stim
outer, inner, horz, vert = get_fixation_stim(win)
fixation_stim_parts = [outer, horz, vert, inner]

# Mask and text for outcomes, properties will be set and reset below
circ_color = [-0.5] * 3
circ_stim = visual.Circle(win,
                          pos=(0, 0),
                          units='deg',
                          fillColor=circ_color,
                          lineColor=circ_color,
                          radius=2.5,
                          edges=128)

txt_color = [0.5] * 3
txt_stim = visual.TextStim(win,
                           units='deg',
                           color=txt_color)


# Start communicating with the serial port
# ========================================
ser = Fake_serial()


# Experiment settings
# ===================
condition = args.condition

max_ntrls = 2  # for the whole experiment
max_nsamples = 30  # per trial
block_size = 1  # number of trials after which to offer a break and feedback
assert max_ntrls % block_size == 0  # need to evenly divide trials into blocks

font = 'Liberation Sans'  # Looks like Arial, but it's free!

toutmask_ms = (1000, 1500)  # time for masking an outcome
toutshow_ms = (1000, 1500)  # time for showing an outcome
tdisplay_ms = (900, 1100)  # delay if "new trial", "error", "final choice"

maxwait_samples = 3  # Maximum seconds we wait for a sample
maxwait_finchoice = 3  # can also be float('inf') to wait forever

keylist_samples = ['s', 'd', 'f', 'x']  # press x to quit
keylist_finchoice = ['s', 'd', 'x']

expected_value_diff = 0.1  # For payoff settings to be used

# Set the fixation_stim colors for signalling state of the experiment
color_standard = (1, 1, 1)  # prompt to do an action
color_newtrl = (0, 1, 0)  # wait: a new trial is starting
color_finchoice = (0, 0, 1)  # wait: next action will be "final choice"
color_error = (1, 0, 0)  # wait: you did an error ... we have to restart


# Start the experimental flow
# ===========================
# Get ready to start the experiment. Start timing from next button press.
txt_stim.text = 'Press any key to start.'
txt_stim.height = 1
txt_stim.font = font
txt_stim.draw()
win.flip()
event.waitKeys()
ser.write(trigger_dict['trig_begin_experiment'])
exp_timer = core.MonotonicClock()
log_data(data_file, onset=exp_timer.getTime(),
         value=trigger_dict['trig_begin_experiment'])
txt_stim.height = 4  # set height for stimuli to be shown below

# Get general payoff settings
payoff_settings = get_payoff_settings(expected_value_diff)

# Start a clock for measuring reaction times
# NOTE: Will be reset to 0 right before recording a button press
rt_clock = core.Clock()

# If we are in the passive condition, load pre-recorded data to replay
if args.condition == 'passive':
    if args.yoke_to:
        yoke_sub = args.yoke_to
    else:
        yoke_sub = args.sub_id
    fname = 'sub-{}_task-spactive_events.tsv'.format(yoke_sub)
    fpath = op.join(data_dir, fname)
    df = pd.read_csv(fpath, sep='\t')
    df = df[pd.notnull(df['trial'])]

current_nblocks = 0
current_ntrls = 0
while current_ntrls < max_ntrls:

    # For each trial, take a new payoff setting
    if condition == 'active':
        payoff_dict, payoff_settings = get_random_payoff_dict(payoff_settings)
        log_data(data_file, onset=exp_timer.getTime(), trial=current_ntrls,
                 payoff_dict=payoff_dict)
    else:  # condition == 'passive'
        payoff_dict = get_payoff_dict(df, current_ntrls)
        log_data(data_file, onset=exp_timer.getTime(), trial=current_ntrls,
                 payoff_dict=payoff_dict)

    # Starting a new trial
    [stim.setAutoDraw(True) for stim in fixation_stim_parts]
    set_fixstim_color(inner, color_newtrl)
    win.callOnFlip(ser.write, trigger_dict['trig_new_trl'])
    frames = get_jittered_waitframes(*tdisplay_ms)
    for frame in range(frames):
        win.flip()
        if frame == 0:
            log_data(data_file, onset=exp_timer.getTime(), trial=current_ntrls,
                     value=trigger_dict['trig_new_trl'], duration=frames)

    # Within this trial, allow sampling
    current_nsamples = 0
    while True:
        # Starting a new sample by setting the fix stim to standard color
        set_fixstim_color(inner, color_standard)
        win.callOnFlip(ser.write, trigger_dict['trig_sample_onset'])
        win.flip()
        rt_clock.reset()
        log_data(data_file, onset=exp_timer.getTime(), trial=current_ntrls,
                 value=trigger_dict['trig_sample_onset'])

        if condition == 'active':
            # Wait for an action of the participant
            keys_rts = event.waitKeys(maxWait=maxwait_samples,
                                      keyList=keylist_samples,
                                      timeStamped=rt_clock)
        else:  # condition == 'passive'
            # Load action from recorded data
            keys_rts = get_passive_action(df, current_ntrls, current_nsamples)
            rt = keys_rts[0][-1]
            # safeguard to never wait for more than maxwait_samples seconds,
            # which is otherwise possible in the first sample of a trial
            if rt >= maxwait_samples:
                rt = np.random.randint(0, maxwait_samples)
            core.wait(rt)  # wait for the time that was the RT

        if not keys_rts:
            if current_nsamples == 0:
                # No keypress in due time: Is this the first sample in the
                # trial? If yes, forgive them and wait for a response forever
                keys_rts = event.waitKeys(maxWait=float('inf'),
                                          keyList=keylist_samples,
                                          timeStamped=rt_clock)
            else:  # Else: raise an error and start new trial
                set_fixstim_color(inner, color_error)
                win.callOnFlip(ser.write, trigger_dict['trig_error'])
                frames = get_jittered_waitframes(*tdisplay_ms)
                for frame in range(frames):
                    win.flip()
                    if frame == 0:
                        # Log an event that we have to disregard all prior
                        # events in this trial
                        log_data(data_file, onset=exp_timer.getTime(),
                                 trial=current_ntrls,
                                 value=trigger_dict['trig_error'],
                                 duration=frames, reset=True)
                # start a new trial without incrementing the trial counter
                break

        # Send trigger
        key, rt = keys_rts[0]
        current_nsamples += 1
        action = keylist_samples.index(key)
        if action == 0 and current_nsamples <= max_nsamples:
            ser.write(trigger_dict['trig_left_choice'])
            value = trigger_dict['trig_left_choice']
        elif action == 1 and current_nsamples <= max_nsamples:
            ser.write(trigger_dict['trig_right_choice'])
            value = trigger_dict['trig_right_choice']
        elif action == 2 and current_nsamples > 1:
            ser.write(trigger_dict['trig_final_choice'])
            value = trigger_dict['trig_final_choice']
        elif action in [0, 1] and current_nsamples > max_nsamples:
            # sampling too much, final choice is being forced
            ser.write(trigger_dict['trig_forced_stop'])
            value = trigger_dict['trig_forced_stop']
            action = 5 if action == 0 else 6
        elif action == 2 and current_nsamples <= 1:
            # premature final choice. will lead to error
            ser.write(trigger_dict['trig_premature_stop'])
            value = trigger_dict['trig_premature_stop']
            action = 7
        elif action == 3:
            core.quit()

        log_data(data_file, onset=exp_timer.getTime(), trial=current_ntrls,
                 action=action, response_time=rt, value=value)

        # Proceed depending on action
        if action in [0, 1] and current_nsamples <= max_nsamples:
            # Display the outcome
            if condition == 'active':
                outcome = np.random.choice(payoff_dict[action])
            else:  # condition == 'passive'
                # note: deduct one off current_nsamples because we already
                # added one (see above) which is to early for this line of code
                outcome = get_passive_outcome(df, current_ntrls,
                                              current_nsamples-1)
            pos = (-5, 0) if action == 0 else (5, 0)
            circ_stim.pos = pos
            txt_stim.pos = pos
            txt_stim.text = str(outcome)
            txt_stim.pos += (0, 0.3)  # manually push text to center of circle

            win.callOnFlip(ser.write, trigger_dict['trig_mask_outcome'])
            frames = get_jittered_waitframes(*toutmask_ms)
            for frame in range(frames):
                circ_stim.draw()
                win.flip()
                if frame == 0:
                    log_data(data_file, onset=exp_timer.getTime(),
                             trial=current_ntrls, duration=frames,
                             value=trigger_dict['trig_mask_outcome'])

            win.callOnFlip(ser.write, trigger_dict['trig_show_outcome'])
            frames = get_jittered_waitframes(*toutshow_ms)
            for frame in range(frames):
                circ_stim.draw()
                txt_stim.draw()
                win.flip()
                if frame == 0:
                    log_data(data_file, onset=exp_timer.getTime(),
                             trial=current_ntrls, duration=frames,
                             outcome=outcome,
                             value=trigger_dict['trig_show_outcome'])

        else:  # action == 2 or current_nsamples > max_nsamples
            # First need to check that a minimum of samples has been taken
            # otherwise, it's an error
            if current_nsamples <= 1:
                set_fixstim_color(inner, color_error)
                win.callOnFlip(ser.write, trigger_dict['trig_error'])
                frames = get_jittered_waitframes(*tdisplay_ms)
                for frame in range(frames):
                    win.flip()
                    if frame == 0:
                        # Log an event that we have to disregard all prior
                        # events in this trial
                        log_data(data_file, onset=exp_timer.getTime(),
                                 trial=current_ntrls,
                                 value=trigger_dict['trig_error'],
                                 duration=frames, reset=True)
                if condition == 'active':
                    # start a new trial without incrementing the trial counter
                    break
                else:  # condition == 'passive'
                    # if a premature stop happens in passive condition, we need
                    # to drop if from the df in order not to enter an endless
                    # loop
                    # # NOTE: We also drop all trials previous to this one ...
                    # They have been replayed, so it should be fine.
                    df = df[df['trial'] >= current_ntrls]
                    # drop rows before and including the *first* encountered
                    # premature stop ... also drop first following event which
                    # indicates the error coloring of the fixation stim ...
                    # retain all other events
                    mask = np.ones(df.shape[0])
                    i = np.where(df['action_type'] == 'premature_stop')[0][0]
                    mask[:i+2] = 0
                    mask = (mask == 1)
                    df = df[mask]
                    break
            # We survived the minimum samples check ...
            # Now get ready for final choice
            set_fixstim_color(inner, color_finchoice)
            win.callOnFlip(ser.write, trigger_dict['trig_new_final_choice'])
            frames = get_jittered_waitframes(*tdisplay_ms)
            for frame in range(frames):
                win.flip()
                if frame == 0:
                    log_data(data_file, onset=exp_timer.getTime(),
                             trial=current_ntrls,
                             value=trigger_dict['trig_new_final_choice'],
                             duration=frames)

            # Switch color of stim cross back to standard: action allowed
            set_fixstim_color(inner, color_standard)
            win.callOnFlip(ser.write, trigger_dict['trig_final_choice_onset'])
            win.flip()
            rt_clock.reset()
            log_data(data_file, onset=exp_timer.getTime(),
                     trial=current_ntrls,
                     value=trigger_dict['trig_final_choice_onset'])

            # Wait for an action of the participant
            keys_rts = event.waitKeys(maxWait=maxwait_finchoice,
                                      keyList=keylist_finchoice,
                                      timeStamped=rt_clock)

            if not keys_rts:
                # No keypress in due time: raise an error and start new trial
                set_fixstim_color(inner, color_error)
                win.callOnFlip(ser.write, trigger_dict['trig_error'])
                frames = get_jittered_waitframes(*tdisplay_ms)
                for frame in range(frames):
                    win.flip()
                    if frame == 0:
                        # Log an event that we have to disregard all prior
                        # events in this trial
                        log_data(data_file, onset=exp_timer.getTime(),
                                 trial=current_ntrls,
                                 value=trigger_dict['trig_error'],
                                 duration=frames, reset=True)
                # start a new trial without incrementing the trial counter
                break

            key, rt = keys_rts[0]
            action = keylist_finchoice.index(key)
            if action == 0:
                ser.write(trigger_dict['trig_left_final_choice'])
                value = trigger_dict['trig_left_final_choice']
            elif action == 1:
                ser.write(trigger_dict['trig_right_final_choice'])
                value = trigger_dict['trig_right_final_choice']
            elif action == 2:
                core.quit()

            # NOTE: add 3 to "action" to distinguish final choice from sampling
            log_data(data_file, onset=exp_timer.getTime(), trial=current_ntrls,
                     action=action+3, response_time=rt, value=value)
            current_nsamples += 1

            # Display final outcome
            outcome = np.random.choice(payoff_dict[action])
            pos = (-5, 0) if action == 0 else (5, 0)
            circ_stim.pos = pos
            txt_stim.pos = pos
            txt_stim.text = str(outcome)
            txt_stim.pos += (0, 0.3)  # manually push text to center of circle

            win.callOnFlip(ser.write, trigger_dict['trig_mask_final_outcome'])
            frames = get_jittered_waitframes(*toutmask_ms)
            for frame in range(frames):
                circ_stim.draw()
                win.flip()
                if frame == 0:
                    log_data(data_file, onset=exp_timer.getTime(),
                             trial=current_ntrls, duration=frames,
                             value=trigger_dict['trig_mask_final_outcome'])

            win.callOnFlip(ser.write, trigger_dict['trig_show_final_outcome'])
            frames = get_jittered_waitframes(*toutshow_ms)
            for frame in range(frames):
                circ_stim.draw()
                txt_stim.draw()
                win.flip()
                if frame == 0:
                    log_data(data_file, onset=exp_timer.getTime(),
                             trial=current_ntrls, duration=frames,
                             outcome=outcome,
                             value=trigger_dict['trig_show_final_outcome'])

            # Is a block finished? If yes, display block feedback and provide
            # a short break
            if (current_ntrls+1) % block_size == 0:
                current_nblocks += 1

                df_tmp = pd.read_csv(data_file, sep='\t')
                outcomes = get_final_choice_outcomes(df_tmp)
                [stim.setAutoDraw(False) for stim in fixation_stim_parts]
                txt_stim.text = ('Block {}/{} done! You earned {} points '
                                 'so far. Remember that your points will be '
                                 'converted to Euros and paid to you at the '
                                 'end of the experiment. '
                                 'Press any key to continue.'
                                 .format(current_nblocks,
                                         int(max_ntrls/block_size),
                                         int(np.sum(outcomes))))
                txt_stim.pos = (0, 0)
                txt_stim.height = 1
                txt_stim.draw()
                win.callOnFlip(ser.write, trigger_dict['trig_end_experiment'])
                win.flip()
                log_data(data_file, onset=exp_timer.getTime(),
                         value=trigger_dict['trig_block_feedback'])
                core.wait(1)  # wait for a bit so that this is not skipped
                event.waitKeys()

                # Reset stim settings for next block
                [stim.setAutoDraw(True) for stim in fixation_stim_parts]
                txt_stim.height = 4  # set height for stimuli to be shown below

            # start the next trial
            current_ntrls += 1
            break

# We are done
[stim.setAutoDraw(False) for stim in fixation_stim_parts]
txt_stim.text = 'This task is over. Press any key to quit.'
txt_stim.pos = (0, 0)
txt_stim.height = 1

txt_stim.draw()
win.callOnFlip(ser.write, trigger_dict['trig_end_experiment'])
win.flip()
log_data(data_file, onset=exp_timer.getTime(),
         value=trigger_dict['trig_end_experiment'])
event.waitKeys()
win.close()
core.quit()
