"""Implement the Sampling Paradigm."""
from psychopy import visual, event, core

from sp_psychopy.utils import (get_fixation_stim, display_message,
                               display_outcome, inquire_action)
from sp_psychopy.define_payoff_distributions import payoff_dict_1
from sp_psychopy.define_ttl_triggers import (trig_begin_experiment,
                                             trig_msg_new_trial,
                                             trig_sample_onset,
                                             trig_left_choice,
                                             trig_right_choice,
                                             trig_final_choice,
                                             trig_mask_outcome,
                                             trig_outcome,
                                             trig_msg_zero_samples,
                                             trig_msg_final_choice,
                                             trig_choice_onset,
                                             trig_left_final_choice,
                                             trig_right_final_choice,
                                             trig_mask_final_outcome,
                                             trig_final_outcome,
                                             trig_end_experiment)


# Open connection to the serial port
class Fake_serial():
    """Convenience class to run the code without true serial connection."""

    def write(self, byte):
        """Take a byte and do nothing."""
        pass


# For now, use a fake serial connection
ser = Fake_serial()

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
ser.write(trig_begin_experiment)
overall_samples = 0
while overall_samples < max_samples_overall:
    # Starting a new trial
    display_message(mywin, ser, 'A new trial has started', 120,
                    trig=trig_msg_new_trial)

    # Display fixation stim
    [stim.setAutoDraw(True) for stim in fixation_stim_parts]
    mywin.callOnFlip(ser.write, trig_sample_onset)
    mywin.flip()

    trial_samples = 0
    trigger_final_choice = False
    while True:

        # A Trial starts by waiting for an action from the participant
        action, rt = inquire_action(mywin, ser, float('Inf'),
                                    trig_left=trig_left_choice,
                                    trig_right=trig_right_choice,
                                    trig_final=trig_final_choice)

        # If sampling action (0 or 1), display the outcome and go on
        if action in [0, 1]:
            display_outcome(mywin, ser, action, payoff_dict_1, 60, 120,
                            trig_mask=trig_mask_outcome,
                            trig_show=trig_outcome)

            # Increment sample counter for this trial
            trial_samples += 1

        # If sampling action 2, or the maximum of sample within a trial has
        # been reached, a final choice should be triggered
        # Afterwards, this trial has ended
        if action == 2 or trigger_final_choice:
            # Intercept if final_choice without having sampled before
            if trial_samples == 0:
                [stim.setAutoDraw(False) for stim in fixation_stim_parts]
                display_message(mywin, ser, 'Take at least one sample before '
                                'your final choice.', 120,
                                trig=trig_msg_zero_samples)
                [stim.setAutoDraw(True) for stim in fixation_stim_parts]
                mywin.flip()
                continue

            # Ask participant to make a final choice
            [stim.setAutoDraw(False) for stim in fixation_stim_parts]
            display_message(mywin, ser, 'Please make your final choice.', 120,
                            trig=trig_msg_final_choice)
            [stim.setAutoDraw(True) for stim in fixation_stim_parts]
            mywin.callOnFlip(ser.write, trig_choice_onset)
            mywin.flip()

            # Wait for the action
            action, rt = inquire_action(mywin, ser, float('Inf'),
                                        keylist=['left', 'right'],
                                        trig_left=trig_left_final_choice,
                                        trig_right=trig_right_final_choice)

            # Display the outcome and start a new trial
            display_outcome(mywin, ser, action, payoff_dict_1, 60, 120,
                            trig_mask=trig_mask_final_outcome,
                            trig_show=trig_final_outcome)
            [stim.setAutoDraw(False) for stim in fixation_stim_parts]
            overall_samples += trial_samples
            break

        # Check if enough samles have been taken to trigger a final choice
        # after the next sample
        if trial_samples + 1 == max_samples_per_trial:
            trigger_final_choice = True

        # Finally, get ready for the next sample within this trial
        mywin.callOnFlip(ser.write, trig_sample_onset)
        mywin.flip()


# We are done!
[stim.setAutoDraw(False) for stim in fixation_stim_parts]
display_message(mywin, ser, 'This task is over. '
                'Press any key to quit.', 1, trig=trig_end_experiment)
event.waitKeys()

# Close the Window and quit
mywin.close()
core.quit()
