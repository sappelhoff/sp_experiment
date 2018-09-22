"""Implement the Sampling Paradigm."""
from psychopy import visual, event

from sp_psychopy.utils import get_fixation_stim


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

# Now the presentation of the stimulus
# Flip the window once per frame
framerate = int(round(mywin.getActualFrameRate()))
present_time = 2  # In seconds
present_frames = present_time * framerate

# Now draw fixation stim
fixation_stim_parts = [outer, horz, vert, inner]
for stim in fixation_stim_parts:
    stim.setAutoDraw(True)  # Draw stim again after each flip

# Actual presentation
for frame in range(present_frames):
    mywin.flip()

# After some time, allow user to close by pressing a button
event.waitKeys()

# Stop drawing the stim
for stim in fixation_stim_parts:
    stim.setAutoDraw(False)

for frame in range(30):
    mywin.flip()


# Close the Window
mywin.close()
