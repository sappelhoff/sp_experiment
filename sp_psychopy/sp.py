"""Implement the Sampling Paradigm."""
from psychopy import visual, event

from sp_psychopy.utils import (get_fixation_stim, display_message,
                               display_outcome, inquire_action)
from sp_psychopy.payoff_distributions import payoff_dict_1


# Define monitor specific window object
mywin = visual.Window(size=[1280, 800],  # Size of window in pixels (x,y)
                      pos=[0, 0],  # X,Y position of window on screen
                      color=[0, 0, 0],  # Background color: RGB [-1,1]
                      fullscr=False,  # Fullscreen for better timing
                      monitor='p51',  # see monitor_definition.py
                      units='deg',
                      winType='pygame')  # Units being used for stimuli


# Get the objects for the fixation stim
outer, inner, horz, vert = get_fixation_stim(mywin)
fixation_stim_parts = [outer, horz, vert, inner]

# On which frame rate are we operating?
fps = int(round(mywin.getActualFrameRate()))
assert fps == 60

# Settings for the experimental flow
max_samples_overall = 10
max_samples_per_trial = 5

# Start the experimental flow
overall_samples = 0
while overall_samples < max_samples_overall:
    # Starting a new trial
    display_message(mywin, 'A new trial has started', 120)

    # Display fixation stim
    [stim.setAutoDraw(True) for stim in fixation_stim_parts]
    mywin.flip()

    trial_samples = 0
    trigger_final_choice = False
    while True:

        # A Trial starts by waiting for an action from the participant
        action, rt = inquire_action(mywin, float('Inf'))

        # If sampling action (0 or 1), display the outcome and go on
        if action in [0, 1]:
            display_outcome(mywin, action, payoff_dict_1, 60, 120)

            # Increment sample counter for this trial
            trial_samples += 1

        # If sampling action 2, or the maximum of sample within a trial has
        # been reached, a final choice should be triggered
        # Afterwards, this trial has ended
        if action == 2 or trigger_final_choice:
            # Intercept if final_choice without having sampled before
            if trial_samples == 0:
                [stim.setAutoDraw(False) for stim in fixation_stim_parts]
                display_message(mywin, 'Take at least one sample before '
                                       'your final choice.', 120)
                [stim.setAutoDraw(True) for stim in fixation_stim_parts]
                mywin.flip()
                continue

            # Ask participant to make a final choice
            [stim.setAutoDraw(False) for stim in fixation_stim_parts]
            display_message(mywin, 'Please make your final choice.', 120)
            [stim.setAutoDraw(True) for stim in fixation_stim_parts]
            mywin.flip()

            # Wait for the action
            action, rt = inquire_action(mywin, float('Inf'),
                                        keylist=['left', 'right'])

            # Display the outcome and start a new trial
            display_outcome(mywin, action, payoff_dict_1, 60, 120)
            [stim.setAutoDraw(False) for stim in fixation_stim_parts]
            overall_samples += trial_samples
            break

        # Check if enough samles have been taken to trigger a final choice
        # after the next sample
        if trial_samples + 1 == max_samples_per_trial:
            trigger_final_choice = True

        # Finally, get ready for the next sample within this trial
        mywin.flip()


# We are done!
[stim.setAutoDraw(False) for stim in fixation_stim_parts]
display_message(mywin, 'This task is over. '
                       'Press any key to quit.', 1)
event.waitKeys()

# Close the Window
mywin.close()
