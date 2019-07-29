[![Build Status](https://dev.azure.com/sappelhoff/sp_experiment/_apis/build/status/sappelhoff.sp_experiment?branchName=master)](https://dev.azure.com/sappelhoff/sp_experiment/_build/latest?definitionId=1&branchName=master)
[![codecov](https://codecov.io/gh/sappelhoff/sp_experiment/branch/master/graph/badge.svg)](https://codecov.io/gh/sappelhoff/sp_experiment)
[![DOI](https://zenodo.org/badge/149852122.svg)](https://zenodo.org/badge/latestdoi/149852122)


# sp_experiment - "Sampling Paradigm Experiment"

The sampling paradigm is an experimental paradigm in which participants are
repeatedly asked to sample from one of many options and observe the outcome.
After some of such samples, the participant can make a *final choice* among the
choice options and receives the outcome of this final draw as a payoff.

The sampling paradigm has close resemblance to the *Pure Exploration* setting
of the multi-armed bandit task.

For more information, see the section on [background literature](README.md#background-literature).

**This Python package implements the sampling paradigm**
- A version *without* optional stopping
- A version *with* optional stopping
- A version where outcomes are not sampled, but shown in "description format"
  - This is not a "sampling paradigm", because there is no sampling between
    the options.

After these three tasks, participants in the study also performed the
[Berlin Numeracy Task](https://www.riskliteracy.org/).

# Installation

This package is intended and tested to run on Microsoft Windows 10.

1. It is recommended to use the Anaconda distribution, see the
[installation instructions](http://docs.continuum.io/anaconda/install/)
2. Then run `conda env create -f environment.yml`
3. Finally, activate the environment and call `pip install -e .` from the
   project root.

# Usage

You can start the experiment by calling `python sp_experiment/sp.py`.

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

The experiment is setup as such that the inputs in the GUI are restricted. More
general settings can be changed in the `define_settings.py` file. Most
importantly, you have to set the `yoke_map`. This is a dictionary that
determines which replay of an active condition a participant sees when they are
in the passive condition.

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

# Makefile

There is also a [`Makefile`](https://github.com/sappelhoff/sp_experiment/blob/master/Makefile)
to simplify several tasks. To make use of it under Windows, install [GNU Make](https://chocolatey.org/packages/make))

# Eyetracking

The script works with a [Tobii 4C eyetracker](https://gaming.tobii.com/product/tobii-eye-tracker-4c/)
(on Microsoft Windows only). You will need the proprietary software
"TobiiProEyeTrackerManager" to be downloaded from the TobiiPro website:
https://www.tobiipro.com/learn-and-support/downloads-pro/. To get all necessary
drivers, you also need to download the "Tobii Eyetracking" software from the
getting started pages: https://gaming.tobii.com/getstarted/

Furthermore, you will need the actual hardware and a "Pro license", which
allows users to access the data on the device. This license needs to be
purchased separately and then loaded onto the specific eyetracker. See this
[form](https://www.tobiipro.com/contact/contact-eyex-for-research/?utm_source=Tobii+Gaming+Contact+form)
by Tobii for more information.

Finally, the interface to Python is done through the Tobii python API:
https://pypi.org/project/tobii-research/

# EEG Triggers

Event markers (also called TTL Triggers) can be sent using the pyserial
library. In our setup we use the [Brain Products Trigger Box](https://pressrelease.brainproducts.com/triggerbox-tips/)
as a device to send serial data via a USB port, which gets transformed into a
parallel TTL signal to be picked up by the EEG amplifier.

See `define_settings.py` and `define_ttl_triggers.py` for more information

# GIT notes:

You may want to git ignore the data files that are produced by running the
experiment. For that, simply add the following text on a new line to the
`.git/info/exclude` file in your clone/fork of the repository:

`experiment_data/`

This will gitignore the folder locally on your machine.

# Details about the file structure

- The `/instructions` directory contains text files of the instructions that
  participants saw
- The `/berlin_numeracy_task` directory contains the BNT that was administered
  in printed form to the participants of the study after completing the
  computerized experiment
- The `sp_experiment` directory is the python module
  - software tests for the paradigm are in `/tests`
  - `/image_data` contains images for the instructions on screen
  - all `.py` files with a `define_` prefix control some aspect ot the
    experimental flow and are imported in the main file `sp.py`
    - the `define_settings.py` contains several important constants
  - `descriptions.py` controls the experimental flow for the "description"
    version of the task
  - `utils.py` contains helper functions


# Background Literature:

1. Meta analysis on the sampling paradigm:
   > Wulff, D. U., Mergenthaler-Canseco, M., & Hertwig, R. (2018). A
   > meta-analytic review of two modes of learning and the
   > description-experiencegap. Psychological Bulletin, 144(2), 140-176.
   > [doi: 10.1037/bul0000115](http://dx.doi.org/10.1037/bul0000115)

1. Original citation of sampling paradigm in behavioral science:
   > Hertwig, R., Barron, G., Weber, E. U., & Erev, I. (2004). Decisions from
   > experience and the effect of rare events in risky choice. Psychological
   > science, 15(8), 534-539.
   > [doi: 10.1111%2Fj.0956-7976.2004.00715.x](https://doi.org/10.1111%2Fj.0956-7976.2004.00715.x)

1. Corresponding ideas in the literature on Mutli-Armed-Bandits
   > Audibert, J. Y., & Bubeck, S. (2010, June). Best arm identification in
   > multi-armed bandits.

   > Bubeck, S., Munos, R., & Stoltz, G. (2009, October). Pure exploration in
   > multi-armed bandits problems. In International conference on Algorithmic
   > learning theory (pp. 23-37). Springer, Berlin, Heidelberg.
