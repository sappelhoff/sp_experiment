"""Simplified experimental flow."""
from psychopy import visual, event, core

from psychopy.tools.monitorunittools import deg2pix

from sp_psychopy.utils import (get_fixation_stim,
                               set_fixstim_color,
                               )

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

# Set the fixation_stim colors for signalling state of the experiment
color_standard = (1, 1, 1)  # prompt to do an action
color_newtrl = (0, 1, 0)  # wait: a new trial is starting
color_finchoice = (0, 0, 1)  # wait: next action will be "final choice"
color_error = (1, 0, 0)  # wait: you did an error ... we have to restart

circ_stim = visual.Circle(win,
                          pos=[242.15028902, 9.68601156],
                          units='pix',
                          fillColor=(-1., -1., -1.),
                          lineColor=(-1., -1., -1.),
                          radius=deg2pix(2.5, win.monitor),
                          edges=128)

# Experiment settings
# ===================
max_ntrls = 2
max_nsamples = 30

font = 'Courier'
font = 'Liberation Sans'

twait_newtrial = 1

maxwait_samples = 10  # Maximum seconds we wait for a sample, if more: error


keylist_samples = ['left', 'right']


# Start the experimental flow
# ===========================
# Get ready to start the experiment. Start timing from next button press.
message = 'Press any key to start.'
txt_stim = visual.TextStim(win,
                           text=message,
                           units='deg',
                           height=1,
                           font=font)
txt_stim.draw()
win.flip()
event.waitKeys()


txt_stim = visual.TextStim(win,
                           text=str(1),
                           pos=(5, 0),
                           units='deg',
                           height=5,
                           color=(1., 1., 1.),
                           font=font)

# Start a clock for measuring reaction times
rt_clock = core.Clock()

current_ntrls = 0
while current_ntrls < max_ntrls:

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

        print(keys_rts)

        # DISPLAY OUTCOME
        key = 1
        while True:
            circ_stim.draw()
            txt_stim.text = str(key)
            txt_stim.draw()
            print(txt_stim.text)
            win.flip()
            print(txt_stim.pos, txt_stim.posPix)
            print(txt_stim.boundingBox)
            prev_key = key
            key = event.waitKeys()
            key = key[0]
            if key == 'up':
                txt_stim.pos += (0, 0.1)
                key = prev_key
            elif key == 'down':
                txt_stim.pos -= (0, 0.1)
                key = prev_key
            elif key == 'left':
                txt_stim.pos -= (0.1, 0)
                key = prev_key
            elif key == 'right':
                txt_stim.pos += (0.1, 0)
                key = prev_key
            elif key in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                txt_stim.setText = str(key)
            elif key == 'x':
                core.quit()
            else:
                print(key)

        # Increment sample counter for this trial
        current_nsamples += 1
        if current_nsamples == max_nsamples:
            current_ntrls += 1
            break
