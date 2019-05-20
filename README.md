[![Build Status](https://travis-ci.org/sappelhoff/sp_experiment.svg?branch=master)](https://travis-ci.org/sappelhoff/sp_experiment)
[![codecov](https://codecov.io/gh/sappelhoff/sp_experiment/branch/master/graph/badge.svg)](https://codecov.io/gh/sappelhoff/sp_experiment)

# Implementing the Sampling Paradigm in PsychoPy

The sampling paradigm is an experimental paradigm in which participants are
repeatedly asked to sample from one of many options and observe the outcome.
After some of such samples, the participant can make a *final choice* among the
choice options and receives the outcome of this final draw as a payoff.

The sampling paradigm has close resemblance to the *Pure Exploration* setting
of the multi-armed bandit task.

# Installation

1. It is recommended to use the Anaconda distribution, see the
[installation instructions](http://docs.continuum.io/anaconda/install/)
2. Then run `conda env create -f environment.yml`
3. Finally, activate the environment and call `pip install -e .` from the
   project root.

# Usage

You can start the experiment by calling `python sp_experiment/sp.py`. Or by
making use of the [`Makefile`](https://github.com/sappelhoff/sp_experiment/blob/master/Makefile)
and calling `make run`.

First, there will be a general navigation to:

1. run the experiment automatically (the full experiment)
1. run the experiment (if only parts should be run)
1. do some test trials
1. calculate bonus money given a participant ID
1. just show some instructions

For the general flow, select `run_experiment`. This will open a GUI that asks
for the following information:

- `ID`: A dropdown menu of integers to select as the unique identifier of a
  participant
- `Age`: A dropdown menu of the participant's potential age
- `Sex`: Dropdown menu to indicate the biological sex of the participant
- `Condition`: Dropdown menu: "Active" or "Passive"

 The experiment is setup as such that the inputs in the GUI are restricted.
 Feel free to adjust.

 Importantly, you have to set the `yoke_map` in the `sp.py` file. This is a
 dictionary that determines which replay of an active condition a participant
 sees when they are in the passive condition.

 Example:
 ```python
yoke_map = {1:1, 2:1}

 ```

Here, the first participant will see a replay of their own active condition
when they perform the passive condition. The second participant will see a
replay of the first participant's active condition. Note that for this to work,
participant 1 HAS to perform the active condition first and the respective data
needs to be present in `sp_experiment/experiment_data` **as saved by the
logger**.

# Eyetracking

The script works with a Tobii 4C eyetracker (WINDOWS only).
You will need the proprietary software "TobiiProEyeTrackerManager" to be
downloaded from https://www.tobiipro.com/learn-and-support/downloads-pro/

And the Tobii 4C eyetracker with a "Pro license" (needs to be purchased
separately and then loaded onto the specific eyetracker).

# GIT notes:

You may want to git ignore the data files that are produced by running the
experiment. For that, simply add the following line to the `.git/info/exclude`
file in your clone/fork of the repository:

`experiment_data/`

This will gitignore the folder locally on your machine.

---
# Background Literature on the Sampling Paradigm:

1. Recent meta-analysis:
   > Wulff, D. U., Mergenthaler-Canseco, M., & Hertwig, R. (2018). A
   meta-analytic review of two modes of learning and the description-experience
   gap. Psychological Bulletin, 144(2), 140-176.
   [http://dx.doi.org/10.1037/bul0000115](http://dx.doi.org/10.1037/bul0000115)

2. One of the original papers introducing it:
   > Hertwig, R., Barron, G., Weber, E. U., & Erev, I. (2004). Decisions from
   experience and the effect of rare events in risky choice. Psychological
   science, 15(8), 534-539. [https://doi.org/10.1111%2Fj.0956-7976.2004.00715.x](https://doi.org/10.1111%2Fj.0956-7976.2004.00715.x)
