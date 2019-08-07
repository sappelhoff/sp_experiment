"""Provide constants for several settings in the experiment."""
import os
from collections import OrderedDict
import serial

import numpy as np

# MASTER SETTINGS
# Set number of participants to record for your study. Must be divisible by 4
n_participants = 40


# Now define a function to create the experimental design for us
def provide_experimental_design(n_participants):
    """Provide an experimental design given some participants.

    Parameters
    ----------
    n_participants : int
        The number of participants in the experiment. Must be divisible by 4.

    Returns
    -------
    yoke_map : collections.OrderedDict
        A dictionary that determines what kind of data participants see in the
        "yoked" condition. Participants are generally either yoked to
        themselves, or to another participant. See also the README.

    opt_stop_map : collections.OrderedDict
        A dictionary that determines whether a participant performs the
        experiment with or without optional stopping. True if with optional
        stopping, False otherwise.

    seed_map : collections.OrderedDict
        A dictionary that determines the payoff_settings to be used for the
        present participant in the "active" condition. The "yoked" (=passive)
        condition will be determined by `yoke_map`

    Notes
    -----
    This will produce a design as follows:

    ID yoke_to condition seed
    1  1       fix       1
    2  2       opt_stop  1
    3  1       fix       1
    4  2       opt_stop  1
    5  5       fix       2
    6  6       opt_stop  2
    7  5       fix       2
    8  6       opt_stop  2
    9  9       fix       3
    ...

    """
    if n_participants % 4 != 0:
        raise ValueError('Your number of subjects MUST be divisible by 4.')

    # Below, we will automatically compute the design of the experiment
    # Set the IDs
    ids = np.arange(1, n_participants+1)

    # Set the yoke_map: Which participant gets yoked to whom
    yokes = np.empty(ids.size, dtype=int)
    yokes[0::4] = ids[::4]
    yokes[1::4] = ids[1::4]
    yokes[2::4] = ids[::4]
    yokes[3::4] = ids[1::4]
    yoke_map = OrderedDict(zip(ids, yokes))

    # Set the condition map: Which participant does optional stopping, and who
    # does not
    opt_stops = np.tile(np.array((False, True)), int(n_participants/2))
    opt_stop_map = OrderedDict(zip(ids, opt_stops))

    # Set the seed map: Controlling the payoff_settings that are generated for
    # each participant
    seeds = np.repeat(np.arange(1, n_participants / 4 + 1), 4)
    seeds = seeds.astype(int)
    seed_map = OrderedDict(zip(ids, seeds))

    return yoke_map, opt_stop_map, seed_map


# And use the function to get the design
yoke_map, opt_stop_map, seed_map = provide_experimental_design(n_participants)

# The expected frames per second. Change depending on your hardware.
EXPECTED_FPS = 60

# Keylists for responses, "__" is a non-existent key serving as a placeholder
KEYLIST_SAMPLES = ['s', 'd', '__', 'x']  # press x to quit
KEYLIST_FINCHOICE = ['s', 'd', 'x']
KEYLIST_DESCRIPTION = ['s', 'd', 'x']
STOP_KEY = 'f'  # used only if condition is optional stopping

# Eyetracking variables
GAZE_TOLERANCE = 0.2  # in psychopy norm units: the window where gaze is OK
GAZE_ERROR_THRESH = 4  # after how many fixation errors to cancel the trial

# Experiment settings
txt_color = (0.45, 0.45, 0.45)
circ_color = (-0.45, -0.45, -0.45)

tfeeddelay_ms = (200, 400)  # time for delaying feedback after an action
toutmask_ms = (800, 800)  # time for masking an outcome ("show blob")
toutshow_ms = (500, 500)  # time for showing an outcome ("show number")
tdisplay_ms = (1000, 1000)  # show color: new trial, error, final choice

expected_value_diff = 0.9  # For payoff settings to be used

# CUTOFF_P is used in get_random_payoff_settings. A negative value will lead
# to a worse balanced set of random payoff settings, a value approaching 1
# will lead to a better balance, but will decrease the pool of options to
# draw randomly from. Middle ground is safe
CUTOFF_P = 0.6

# Set the fixation_stim colors for signalling state of the experiment
color_standard = txt_color  # prompt for an action
color_newtrl = (0, 1, 0)  # wait: a new trial is starting
color_finchoice = (0, 0, 1)  # wait: next action will be "final choice"
color_error = (1, 0, 0)  # wait: you did an error ... we have to restart

# EXPERIMENT SETTINGS,  including yoke_map to determine which participant
# gets yoked to which
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
ser = "COM4"  # either address to serial port or None ... COM4
if isinstance(ser, str):
    # Try to open a serial port
    try:
        ser = serial.Serial(ser)

    # If it doesn't work, raise an error ... except when we are on
    # Azure Pipelines for the CI testing. ('Agent.Id' is defined there.)
    except serial.SerialException as ee:
        agent_id = os.getenv('AZURE_PIPELINE', False)
        if not agent_id:
            raise ee
        else:
            print('serial "{}" does not exist. Not raising an error, assuming '
                  'we are on Azure Pipelines with Agend.Id={}'
                  .format(ser, agent_id))

# When sending EEG trigger signals / event markers it is important to "reset"
# the serial port to zero after each sent byte. The time between the sent byte
# and the resetting must be long enough so that the sampling rate of the EEG
# system can pick up the change in signals. E.g., for a 1000Hz sampling
# frequency, the trigger MUST be on for at least 1ms ... better for 2 or 3.
# `WAITSECS` determines for how long triggers will be ON.
# NOTE: `WAITSECS` should NOT be longer than the time the screen needs to
# refresh, because we time our experimental presentations per frames and
# window flips. If `WAITSECS` is longer than a flip takes, the following flip
# will be delayed. Flip times for 60Hz=16.6mss, 120Hz=8.3ms, 144Hz=6.9ms
WAITSECS = 0.002

# Settings for sp task in all conditions
# if no optional stopping, participants will always play `max_nsamples`
# samples ... else, they can stop after a minimum of 1 sample ... or before
# they have taken a maximum of `max_nsamples
max_nsamples_opt_stop = 19
max_nsamples = 12
max_ntrls = 100
block_size = 20

# Settings for training
test_max_ntrls = 2  # Up to a maximum of 5 ... bounded by sub-999 test file
test_max_nsamples_opt_stop = max_nsamples_opt_stop
test_max_nsamples = max_nsamples
test_block_size = test_max_ntrls

# In description
DESCR_EXPERIENCED = True  # Show experienced lotteries?
fraction_to_run = 1.  # what fraction of all trials to run?
color_magnitude = (1, 0, 1)
color_probability = (0, 0, 1)
