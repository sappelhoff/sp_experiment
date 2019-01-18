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

you can start the experiment from the command line. There are two required
arguments:

- `--condition` (can be active, or passive)
- `--sub_id` (should be a number)

There is one optional argument:

- `--yoke_to` (should point to a previous sub_id, defaults to `--sub_id`)

```bash
# from the project root
# active condition of participant 1
python sp_experiment/sp.py --condition active --sub_id 1

# passive condition of participant 1, seeing the replay of participant 1
# NOTE: you can use abbreviations -c and -s, ...
python sp_experiment/sp.py -c active -s 1

# passive condition of participant 2, seeing a replay of participant 1
# NOTE: can also use -y instead of --yoke_to
python sp_experiment/sp.py -c passive -s 2 --yoke_to 1

# or use the Makefile for a test run:
make active-test-run

# passive test run only works, if data from active test run is present
make passive-test-run

# Clean up test data
make clean-test-experiment-data
```

# Instructions to participants

All participants should read this instruction text and should also be allowed
to perform some test trials until they have fully understood the paradigm.

see [participant_instructions](./participant_instuctions)

---
# Background Literature on the Sampling Paradigm:

1. recent meta-analysis:
   > Wulff, D. U., Mergenthaler-Canseco, M., & Hertwig, R. (2018). A meta-analytic review of two modes of learning and the description-experience gap. Psychological Bulletin, 144(2), 140-176. http://dx.doi.org/10.1037/bul0000115

2. original paper introducing it:
   > Hertwig, R., Barron, G., Weber, E. U., & Erev, I. (2004). Decisions from experience and the effect of rare events in risky choice. Psychological science, 15(8), 534-539. https://doi.org/10.1111%2Fj.0956-7976.2004.00715.x
