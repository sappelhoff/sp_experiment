"""Simplified experimental flow."""
import numpy as np
from psychopy import visual, event, core

from sp_psychopy.utils import (get_fixation_stim,
                               set_fixstim_color,
                               )

from sp_psychopy.define_payoff_distributions import (get_payoff_settings,
                                                     get_random_payoff_dict)
# Get PsychoPy stimuli ready
# ==========================

# Define monitor specific window object
win = visual.Window(size=[1280, 800],  # Size of window in pixels (x,y)
                    pos=[0, 0],  # X,Y position of window on screen
                    color=(0, 0, 0),  # Background color: RGB [-1,1]
                    fullscr=False,  # Fullscreen for better timing
                    monitor='p51',  # see monitor_definition.py
                    units='deg',
                    winType='pyglet')  # Units being used for stimuli

# Get the objects for the fixation stim
outer, inner, horz, vert = get_fixation_stim(win)
fixation_stim_parts = [outer, horz, vert, inner]

# Mask and text for outcomes, properties will be set and reset below
circ_stim = visual.Circle(win,
                          pos=(0, 0),
                          units='deg',
                          fillColor=(-1., -1., -1.),
                          lineColor=(-1., -1., -1.),
                          radius=2.5,
                          edges=128)

txt_stim = visual.TextStim(win,
                           units='deg',
                           color=(1., 1., 1.))


# Experiment settings
# ===================
max_ntrls = 2
max_nsamples = 3

font = 'Liberation Sans'  # Looks like Arial, but it's free!

twait_newtrial = 1
twait_finchoice = 1
twait_error = 1

maxwait_samples = 10  # Maximum seconds we wait for a sample, if more: error
maxwait_finchoice = 10

mask_frames = 30
show_frames = 30

keylist_samples = ['left', 'right', 'down', 'x']  # press x to quit
keylist_finchoice = ['left', 'right']

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
txt_stim.height = 5  # set height for stimuli to be shown below

# Get general payoff settings
payoff_settings = get_payoff_settings(expected_value_diff)

# Start a clock for measuring reaction times
rt_clock = core.Clock()

current_ntrls = 0
while current_ntrls < max_ntrls:

    # For each trial, take a new payoff setting
    payoff_dict, payoff_settings = get_random_payoff_dict(payoff_settings)

    # Starting a new trial
    [stim.setAutoDraw(True) for stim in fixation_stim_parts]
    set_fixstim_color(inner, color_newtrl)
    win.flip()
    core.wait(twait_newtrial)

    # Within this trial, allow sampling
    current_nsamples = 0
    while True:
        # Starting a new sample by setting the fix stim to standard color
        set_fixstim_color(inner, color_standard)
        win.callOnFlip(rt_clock.reset)
        win.flip()

        # Wait for an action of the participant
        keys_rts = event.waitKeys(maxWait=maxwait_samples,
                                  keyList=keylist_samples,
                                  timeStamped=rt_clock)

        assert len(keys_rts) == 1
        key, rt = keys_rts[0]
        action = keylist_samples.index(key)
        current_nsamples += 1

        # Based on the action, continue
        if action == 3:
            core.quit()

        elif action in [0, 1] and current_nsamples <= max_nsamples:
            # Display the outcome
            outcome = np.random.choice(payoff_dict[action])
            pos = (-5, 0) if action == 0 else (5, 0)
            circ_stim.pos = pos
            txt_stim.pos = pos
            txt_stim.text = str(outcome)
            txt_stim.pos += (0, 0.3)  # manually push text to center of circle

            for frame in range(mask_frames):
                circ_stim.draw()
                win.flip()

            for frame in range(show_frames):
                circ_stim.draw()
                txt_stim.draw()
                win.flip()

        else:  # action == 2 or current_nsamples == max_nsamples
            # First need to check that a minimum of samples has been taken
            if current_nsamples <= 1:
                set_fixstim_color(inner, color_error)
                win.flip()
                core.wait(twait_error)
                # start a new trial without incrementing the trial counter
                break
            # We survived the minimum samples check ...
            # Now get ready for final choice
            set_fixstim_color(inner, color_finchoice)
            win.flip()
            core.wait(twait_finchoice)

            # Switch color of stim cross back to standard: action allowed
            set_fixstim_color(inner, color_standard)
            win.callOnFlip(rt_clock.reset)
            win.flip()

            # Wait for an action of the participant
            keys_rts = event.waitKeys(maxWait=maxwait_finchoice,
                                      keyList=keylist_finchoice,
                                      timeStamped=rt_clock)

            assert len(keys_rts) == 1
            key, rt = keys_rts[0]
            action = keylist_samples.index(key)

            # Display final outcome
            outcome = np.random.choice(payoff_dict[action])
            pos = (-5, 0) if action == 0 else (5, 0)
            circ_stim.pos = pos
            txt_stim.pos = pos
            txt_stim.text = str(outcome)
            txt_stim.pos += (0, 0.3)  # manually push text to center of circle

            for frame in range(mask_frames):
                circ_stim.draw()
                win.flip()

            for frame in range(show_frames):
                circ_stim.draw()
                txt_stim.draw()
                win.flip()

            # This trial is done, start the next one
            current_ntrls += 1
            break

# We are done
[stim.setAutoDraw(False) for stim in fixation_stim_parts]
txt_stim.text = 'This task is over. Press any key to quit.'
txt_stim.pos = (0, 0)
txt_stim.height = 1

txt_stim.draw()
win.flip()
event.waitKeys()
win.close()
core.quit()
