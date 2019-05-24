"""Provide constants for several settings in the experiment."""
from collections import OrderedDict

# CONSTANTS
# The expected frames per second. Change depending on your hardware.
EXPECTED_FPS = 60

# Keylists for responses
# replace "__" with "f" to allow final choices
KEYLIST_SAMPLES = ['s', 'd', '__', 'x']  # press x to quit
KEYLIST_FINCHOICE = ['s', 'd', 'x']
KEYLIST_DESCRIPTION = ['s', 'd', 'x']

# Eyetracking variables
GAZE_TOLERANCE = 0.1  # in psychopy norm units: the window where gaze is OK
GAZE_ERROR_THRESH = 4  # after how many fixation errors to cancel the trial

# Experiment settings
txt_color = (0.45, 0.45, 0.45)
circ_color = (-0.45, -0.45, -0.45)

tfeeddelay_ms = (200, 400)  # time for delaying feedback after an action
toutmask_ms = (800, 800)  # time for masking an outcome ("show blob")
toutshow_ms = (500, 500)  # time for showing an outcome ("show number")
tdisplay_ms = (1000, 1000)  # show color: new trial, error, final choice

expected_value_diff = 0.9  # For payoff settings to be used

# Set the fixation_stim colors for signalling state of the experiment
color_standard = txt_color  # prompt for an action
color_newtrl = (0, 1, 0)  # wait: a new trial is starting
color_finchoice = (0, 0, 1)  # wait: next action will be "final choice"
color_error = (1, 0, 0)  # wait: you did an error ... we have to restart

# EXPERIMENT SETTINGS,  including yoke_map to determine which participant
# gets yoked to which
twait_show_instr = 0  # how long to force instruction screen
monitor = 'room26'
ser = None  # either address to serial port or None
maxwait = 3
exchange_rate = 0.005
lang = 'de'
font = 'Liberation Sans'

max_ntrls = 1
max_nsamples = 2
block_size = 1
# Settings for training
test_max_ntrls = 1
test_max_nsamples = 1
test_block_size = 1

# First 10 subjs are mapped to themselves
yoke_map = OrderedDict(zip(list(range(1, 11)), list(range(1, 11))))
# Next 10 are mapped to first ten
for i, j in zip(list(range(11, 21)), list(range(1, 11))):
    yoke_map[i] = j

# In description: Show experienced lotteries?
DESCR_EXPERIENCED = True
