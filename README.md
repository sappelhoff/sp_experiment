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
arguments: `--condition` (can be active, or passive), and `--sub_id` (should be
a number).

```bash
# from the project root
python sp_psychopy/sp.py --condition active --sub_id 1

# or use the [Makefile](./Makefile) for a test run:
make clean-test-experiment-data
make start-test-experiment
```

# Instructions to participants

All participants should read this instruction text and should also be allowed
to perform some test trials until they have fully understood the paradigm.

## German
TBD

## English
TBD

---
# Background Literature on the Sampling Paradigm:

1. Wulff, D. U., Mergenthaler-Canseco, M., & Hertwig, R. (2018). A meta-analytic review of two modes of learning and the description-experience gap. Psychological Bulletin, 144(2), 140-176. http://dx.doi.org/10.1037/bul0000115

2. Hertwig, R., Barron, G., Weber, E. U., & Erev, I. (2004). Decisions from experience and the effect of rare events in risky choice. Psychological science, 15(8), 534-539. https://doi.org/10.1111%2Fj.0956-7976.2004.00715.x
