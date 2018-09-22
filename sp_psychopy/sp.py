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

# Starting a new sequence
display_message(mywin, 'A new sequence has started', 120)

# Display fixation stim
[stim.setAutoDraw(True) for stim in fixation_stim_parts]
mywin.flip()

for trial in range(5):
    # A Trial starts by waiting for a response
    action, rt = inquire_action(mywin, 'inf')

    # As soon as we got one, display the outcome
    display_outcome(mywin, action, payoff_dict_1, 60, 120)

    # Then get ready for the next trial
    mywin.flip()

# After some time, allow user to close by pressing a button
event.waitKeys()

# Close the Window
mywin.close()
