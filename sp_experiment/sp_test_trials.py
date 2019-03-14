"""Provide a simple flow of test trials."""
import numpy as np
from psychopy import visual, event, core

from sp_experiment.utils import (set_fixstim_color,
                                 get_jittered_waitframes)
from sp_experiment.define_payoff_settings import (get_payoff_settings,
                                                  get_random_payoff_dict)
from sp_experiment.psychopy_utils import get_fixation_stim

# Experiment settings
font = 'Liberation Sans'  # Looks like Arial, but it's free!
expected_value_diff = 0.1  # For payoff settings to be used

max_nsamples = 12  # per trial
max_ntrls = 1  # for the whole experiment

toutmask_ms = (600, 1000)  # time for masking an outcome
toutshow_ms = (800, 1200)  # time for showing an outcome
tdisplay_ms = (900, 1100)  # delay if "new trial", "error", "final choice"

maxwait_samples = 3  # Maximum seconds we wait for a sample
maxwait_finchoice = 3  # can also be float('inf') to wait forever

# replace "__" with "f" to allow final choices
keylist_samples = ['s', 'd', '__', 'x']  # press x to quit
keylist_finchoice = ['s', 'd', 'x']

color_standard = (1, 1, 1)  # prompt to do an action
color_newtrl = (0, 1, 0)  # wait: a new trial is starting
color_finchoice = (0, 0, 1)  # wait: next action will be "final choice"
color_error = (1, 0, 0)  # wait: you did an error ... we have to restart


def run_test_trials():
    """Simplified test trials."""
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

    # Start the experimental flow
    # ===========================
    # Get ready to start the experiment. Start timing from next button press.
    txt_stim.text = ('Welcome to the test trials. You will start with a '
                     'trial in the "active" condition. You can freely sample '
                     'for {} times and then make a final choice. Press any '
                     'key to start.'.format(max_nsamples))
    txt_stim.height = 1
    txt_stim.font = font
    txt_stim.draw()
    win.flip()
    event.waitKeys()

    txt_stim.height = 4  # set height for stimuli to be shown below

    # Get general payoff settings
    payoff_settings = get_payoff_settings(expected_value_diff)

    current_ntrls = 0
    while current_ntrls < max_ntrls:

        payoff_dict, payoff_settings = get_random_payoff_dict(payoff_settings)

        # Starting a new trial
        [stim.setAutoDraw(True) for stim in fixation_stim_parts]
        set_fixstim_color(inner, color_newtrl)
        frames = get_jittered_waitframes(*tdisplay_ms)
        for frame in range(frames):
            win.flip()

        # Within this trial, allow sampling
        current_nsamples = 0
        while True:
            # Starting a new sample by setting the fix stim to standard color
            set_fixstim_color(inner, color_standard)
            win.flip()

            # Wait for an action of the participant
            keys_rts = event.waitKeys(maxWait=maxwait_samples,
                                      keyList=keylist_samples,
                                      timeStamped=True)

            if not keys_rts:
                if current_nsamples == 0:
                    # No keypress in due time: Is this the first sample in the
                    # trial? If yes, forgive them and wait for a response
                    # forever
                    keys_rts = event.waitKeys(maxWait=float('inf'),
                                              keyList=keylist_samples,
                                              timeStamped=True)
                else:  # Else: raise an error and start new trial
                    set_fixstim_color(inner, color_error)
                    frames = get_jittered_waitframes(*tdisplay_ms)
                    for frame in range(frames):
                        win.flip()
                    # start a new trial without incrementing the trial counter
                    break

            # Send trigger
            key, rt = keys_rts[0]
            current_nsamples += 1
            action = keylist_samples.index(key)
            if action == 3 and current_nsamples <= max_nsamples:
                core.quit()

            # Proceed depending on action
            if action in [0, 1] and current_nsamples <= max_nsamples:
                # Display the outcome
                outcome = np.random.choice(payoff_dict[action])
                pos = (-5, 0) if action == 0 else (5, 0)
                circ_stim.pos = pos
                txt_stim.pos = pos
                txt_stim.text = str(outcome)
                txt_stim.pos += (0, 0.3)  # manually push txt to center
                frames = get_jittered_waitframes(*toutmask_ms)
                for frame in range(frames):
                    circ_stim.draw()
                    win.flip()

                frames = get_jittered_waitframes(*toutshow_ms)
                for frame in range(frames):
                    circ_stim.draw()
                    txt_stim.draw()
                    win.flip()

            else:  # action == 2 or current_nsamples > max_nsamples
                # Now get ready for final choice
                set_fixstim_color(inner, color_finchoice)
                frames = get_jittered_waitframes(*tdisplay_ms)
                for frame in range(frames):
                    win.flip()

                # Switch color of stim cross back to standard: action allowed
                set_fixstim_color(inner, color_standard)
                win.flip()

                # Wait for an action of the participant
                keys_rts = event.waitKeys(maxWait=maxwait_finchoice,
                                          keyList=keylist_finchoice,
                                          timeStamped=True)

                if not keys_rts:
                    # No keypress in due time: raise an error and start new trl
                    set_fixstim_color(inner, color_error)
                    frames = get_jittered_waitframes(*tdisplay_ms)
                    for frame in range(frames):
                        win.flip()
                    # start a new trial without incrementing the trial counter
                    break

                key, rt = keys_rts[0]
                action = keylist_finchoice.index(key)
                if action == 2:
                    core.quit()

                current_nsamples += 1

                # Display final outcome
                outcome = np.random.choice(payoff_dict[action])
                pos = (-5, 0) if action == 0 else (5, 0)
                circ_stim.pos = pos
                txt_stim.pos = pos
                txt_stim.text = str(outcome)
                txt_stim.pos += (0, 0.3)  # manually push text to center

                frames = get_jittered_waitframes(*toutmask_ms)
                for frame in range(frames):
                    circ_stim.draw()
                    win.flip()

                frames = get_jittered_waitframes(*toutshow_ms)
                for frame in range(frames):
                    circ_stim.draw()
                    txt_stim.draw()
                    win.flip()

                # start the next trial
                current_ntrls += 1
                break
