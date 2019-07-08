"""Provide constants for several settings in the experiment."""
from collections import OrderedDict
import serial

# Set whether participants can stop or HAVE to do a certain number of samples
# per trial
OPTIONAL_STOPPING = False

# The expected frames per second. Change depending on your hardware.
EXPECTED_FPS = 60

# Keylists for responses, "__" is a non-existent key serving as a placeholder
KEYLIST_SAMPLES = ['s', 'd', '__', 'x']  # press x to quit
KEYLIST_FINCHOICE = ['s', 'd', 'x']
KEYLIST_DESCRIPTION = ['s', 'd', 'x']
if OPTIONAL_STOPPING:
    # If we allow optional stopping, make pressing the "F" key an option
    idx_to_replace = KEYLIST_SAMPLES.index('__')
    KEYLIST_SAMPLES[idx_to_replace] = 'f'

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
monitor = 'room26'  # see define_monitors.py
maxwait = 3  # how long to wait before each action ... if longer: timeout
exchange_rate = 0.005  # multiply this with accumulated points to get Euros
lang = 'de'
font = 'Liberation Sans'

# Serial port
# INSTRUCTIONS TRIGGER BOX
# https://www.brainproducts.com/downloads.php?kid=40
# Open the Windows device manager,
# search for the "TriggerBox VirtualSerial Port (COM6)"
# in "Ports /COM & LPT)" and enter the COM port number in the constructor.
# If there is no TriggerBox, set ser to None
ser = None  # either address to serial port or None ... COM4
waittime = 0.005  # how long to keep up a signal before resetting to zero
if isinstance(ser, str):
    ser = serial.Serial(ser)

# Settings for sp task in all conditions
# if OPTIONAL_STOPPING is False, participants will always play `max_nsamples`
# samples ... else, they can stop after a minimum of 1 sample ... or before
# they have taken a maximum of `max_nsamples
if OPTIONAL_STOPPING:
    max_nsamples = 20
else:
    max_nsamples = 12
max_ntrls = 100
block_size = 20

# Settings for training
test_max_ntrls = 2  # Up to a maximum of 5 ... bounded by sub-999 test file
test_max_nsamples = max_nsamples
test_block_size = test_max_ntrls

# First 10 subjs are mapped to themselves
yoke_map = OrderedDict(zip(list(range(1, 11)), list(range(1, 11))))
# Next 10 are mapped to first ten
for i, j in zip(list(range(11, 21)), list(range(1, 11))):
    yoke_map[i] = j

# In description
DESCR_EXPERIENCED = True  # Show experienced lotteries?
fraction_to_run = 1.  # what fraction of all trials to run?
color_magnitude = (1, 0, 1)
color_probability = (0, 0, 1)
