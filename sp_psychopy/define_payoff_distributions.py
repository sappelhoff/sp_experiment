"""Provide the payoff distributions to be used in the Sampling Paradigm.

main file: sp.py

For more information, see also the following keys within the
"task-sp_events.json" file: action_type, action, outcome

"""

# Payoff 1
payoff_dict_1 = {}
payoff_dict_1[0] = [0] * 7 + [1] * 3
payoff_dict_1[1] = [0] * 3 + [1] * 7
