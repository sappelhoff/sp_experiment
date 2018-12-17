"""Implement the Sampling Paradigm.

This is the main file.

see 'define_monitors.py' to first define a suitable monitor, which to then add
in the mywin = visual.Window call.

see 'define_payoff_distributions.py' for a closer look at the environments
where subjects have to make choices during this EEG experiment.

see 'define_ttl_triggers.py' for extensive comments on the meaning of the TTL
trigger values to be sent during the EEG experiment. You can also change the
byte values if you want to.

see task-sp_events.json' for a json dictionary explaining the variables that
are collected with this experiment code.

There are some necessary adjustments based on the used hardware. Just search
the script for the following lines and adjust to your needs:
1. assert fps ==   # adjust to your framerate is and also change in utils.py
2. ser =   # pass a true serial connection to it for TTL markers
3. monitor=  # check define_monitors.py to define your own monitor

Furthermore, you might want to change some parameters of the experiment. Apart
from the secondary files mentioned further above, the following lines in this
script are relevant to that end:
# for samples/trial numbers
1. max_samples_overall =   # maximum samples in the sampling paradigm task
2. max_samples_per_trial =   # maximum samples before final choice triggered

# for timings ... either stable or within a uniform range [min, max]
3. tdisplay_secs =   # stable display time for messages
4. post_action_jitter_secs =   # jitter after action before continue
5. toutmask_secs =   # jitter masking the outcome
6. toutshow_secs =   # jitter showing the outcome


"""
import os
import os.path as op
import argparse

from psychopy import visual, event, core

import sp_psychopy
from sp_psychopy.utils import (font,
                               get_fixation_stim,
                               set_fixstim_color,
                               display_message,
                               display_outcome,
                               inquire_action,
                               log_data,
                               tw_jit,
                               utils_fps,
                               Fake_serial)
from sp_psychopy.define_payoff_distributions import (get_payoff_settings,
                                                     get_random_payoff_dict)
from sp_psychopy.define_ttl_triggers import (trig_begin_experiment,
                                             trig_new_trl,
                                             trig_sample_onset,
                                             trig_left_choice,
                                             trig_right_choice,
                                             trig_final_choice,
                                             trig_mask_outcome,
                                             trig_show_outcome,
                                             trig_msg_zero_samples,
                                             trig_new_final_choice,
                                             trig_final_choice_onset,
                                             trig_left_final_choice,
                                             trig_right_final_choice,
                                             trig_mask_final_outcome,
                                             trig_show_final_outcome,
                                             trig_end_experiment)

# Prepare for logging all experimental variables of interest
# Parse the subject ID
parser = argparse.ArgumentParser()
parser.add_argument('--sub_id', '-s', type=str, required=True)
args = parser.parse_args()

# BIDS data file name
fname = 'sub-{}_task-sp_events.tsv'.format(args.sub_id)

# Check directory is present and file name not yet used
init_dir = op.dirname(sp_psychopy.__file__)
data_dir = op.join(init_dir, 'experiment_data')
if not op.exists(data_dir):
    os.mkdir(data_dir)

data_file = op.join(data_dir, fname)
if op.exists(data_file):
    raise OSError('A data file for {} '
                  'already exists: {}'.format(args.sub_id, data_file))

# Write an initial header to the tab separated log file
# For a description of the keys, see the "task-sp_events.json" file.
variables = ['onset', 'duration', 'action_type', 'action', 'outcome',
             'response_time', 'event_value']

with open(data_file, 'w') as fout:
    header = '\t'.join(variables)
    fout.write(header + '\n')

# For now, use a fake serial connection
ser = Fake_serial()

# Define monitor specific window object
mywin = visual.Window(size=[1280, 800],  # Size of window in pixels (x,y)
                      pos=[0, 0],  # X,Y position of window on screen
                      color=[0, 0, 0],  # Background color: RGB [-1,1]
                      fullscr=False,  # Fullscreen for better timing
                      monitor='p51',  # see monitor_definition.py
                      units='deg',
                      winType='pyglet')  # Units being used for stimuli


# Get the objects for the fixation stim
outer, inner, horz, vert = get_fixation_stim(mywin)
fixation_stim_parts = [outer, horz, vert, inner]

# Set the fixation_stim colors for starting a new trial, final choice, and an
# error (e.g., have to take more than one sample)
color_standard = (1, 1, 1)
color_newtrl = (0, 1, 0)
color_finchoice = (0, 0, 1)
color_error = (1, 0, 0)

set_fixstim_color(inner, color_newtrl)

# On which frame rate are we operating?
fps = int(round(mywin.getActualFrameRate()))
assert fps == 60
if utils_fps != fps:
    raise ValueError('Please adjust the utils_fps variable in utils.py')

# Settings for the experimental flow
max_samples_overall = 60
max_samples_per_trial = 30
tdisplay_secs = 2.
toutmask_secs = [0.5, 0.75]
toutshow_secs = [0.6, 0.8]

# Get payoff settings to be used
expected_value_diff = 0.1
payoff_settings = get_payoff_settings(expected_value_diff)

# Get ready to start the experiment. Start timing from next button press.
message = 'Press any key to start.'
txt_stim = visual.TextStim(mywin,
                           text=message,
                           units='deg',
                           height=1,
                           font=font)
txt_stim.draw()
mywin.flip()
mywin.callOnFlip(ser.write, trig_begin_experiment)
event.waitKeys()
mywin.flip()
timer = core.MonotonicClock()
log_data(data_file, onset=timer.getTime(),
         event_value=trig_begin_experiment)

# Separate timer for collecting reaction times
t_rt = core.Clock()

# Start the experimental flow
overall_samples = 0
while overall_samples < max_samples_overall:
    # Starting a new trial
    trial_samples = 0
    trigger_final_choice = False
    display_message(mywin, ser, data_file, timer, 'A new trial has started',
                    frames=int(tdisplay_secs*fps), trig=trig_new_trl)

    # For each trial, we use a new payoff setting
    # reassign payoff_settings to same without currently used setting
    # (no replacement)
    payoff_dict, payoff_settings = get_random_payoff_dict(payoff_settings)

    # Display fixation stim
    [stim.setAutoDraw(True) for stim in fixation_stim_parts]
    mywin.callOnFlip(ser.write, trig_sample_onset)
    mywin.flip()
    # Start a timer to measure reaction time
    t_rt.reset()

    # Quickly log data before concentrating on reaction of participant
    log_data(data_file, onset=timer.getTime(),
             event_value=trig_sample_onset)

    while True:

        # A Trial starts by waiting for an action from the participant
        action, rt = inquire_action(mywin, ser, data_file, timer, t_rt,
                                    timeout=float('Inf'), final=False,
                                    trig_left=trig_left_choice,
                                    trig_right=trig_right_choice,
                                    trig_final=trig_final_choice)

        # If sampling action (0 or 1), display the outcome and go on
        if action in [0, 1]:
            outcome = display_outcome(mywin, ser, data_file, timer, action,
                                      payoff_dict,
                                      mask_frames=tw_jit(toutmask_secs[0]*fps,
                                                         toutmask_secs[1]*fps),
                                      show_frames=tw_jit(toutshow_secs[0]*fps,
                                                         toutshow_secs[1]*fps),
                                      trig_mask=trig_mask_outcome,
                                      trig_show=trig_show_outcome)

            # Increment sample counter for this trial
            trial_samples += 1

        # If sampling action 2, or the maximum of sample within a trial has
        # been reached, a final choice should be triggered
        # Afterwards, this trial has ended
        if action == 2 or trigger_final_choice:
            # Intercept if final_choice without having sampled before
            if trial_samples == 0:
                [stim.setAutoDraw(False) for stim in fixation_stim_parts]
                display_message(mywin, ser, data_file, timer,
                                'Take at least one sample before '
                                'your final choice.',
                                frames=int(tdisplay_secs*fps),
                                trig=trig_msg_zero_samples)
                [stim.setAutoDraw(True) for stim in fixation_stim_parts]
                mywin.flip()
                continue

            # Ask participant to make a final choice
            [stim.setAutoDraw(False) for stim in fixation_stim_parts]
            display_message(mywin, ser, data_file, timer,
                            'Please make your final choice.',
                            frames=int(tdisplay_secs*fps),
                            trig=trig_new_final_choice)
            [stim.setAutoDraw(True) for stim in fixation_stim_parts]
            mywin.callOnFlip(ser.write, trig_final_choice_onset)
            mywin.flip()
            # Start a timer to measure reaction time
            t_rt.reset()

            # Quickly log data before concentrating on reaction of participant
            log_data(data_file, onset=timer.getTime(),
                     event_value=trig_final_choice_onset)

            # Wait for the action
            action, rt = inquire_action(mywin, ser, data_file, timer, t_rt,
                                        timeout=float('Inf'), final=True,
                                        keylist=['left', 'right'],
                                        trig_left=trig_left_final_choice,
                                        trig_right=trig_right_final_choice)

            # Display the outcome
            outcome = display_outcome(mywin, ser, data_file, timer, action,
                                      payoff_dict,
                                      mask_frames=tw_jit(toutmask_secs[0]*fps,
                                                         toutmask_secs[1]*fps),
                                      show_frames=tw_jit(toutshow_secs[0]*fps,
                                                         toutshow_secs[1]*fps),
                                      trig_mask=trig_mask_final_outcome,
                                      trig_show=trig_show_final_outcome)
            [stim.setAutoDraw(False) for stim in fixation_stim_parts]
            overall_samples += trial_samples

            # Start a new trial
            break

        # Check if enough samles have been taken to trigger a final choice
        # after the next sample
        if trial_samples + 1 == max_samples_per_trial:
            trigger_final_choice = True

        # Finally, get ready for the next sample within this trial
        mywin.callOnFlip(ser.write, trig_sample_onset)
        mywin.flip()

        # Start a timer to measure reaction time
        t_rt.reset()

        # Quickly log data before concentrating on reaction of participant
        log_data(data_file, onset=timer.getTime(),
                 event_value=trig_sample_onset)


# We are done!
[stim.setAutoDraw(False) for stim in fixation_stim_parts]
mywin.callOnFlip(ser.write, trig_end_experiment)
mywin.flip()
log_data(data_file, onset=timer.getTime(),
         event_value=trig_end_experiment)

message = 'This task is over. Press any key to quit.'
txt_stim.text = message
txt_stim.draw()
mywin.flip()
event.waitKeys()
txt_stim = None

# Close the Window and quit
mywin.close()
core.quit()
