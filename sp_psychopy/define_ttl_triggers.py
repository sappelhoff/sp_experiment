"""Definitions for the TTL triggers to be sent.

main file: sp.py

For more information, see also the "event_value" key within the
"task-sp_events.json" file.

"""

# At the beginning and end of the experiment ... take these triggers to crop
# the meaningful EEG data. Make sure to include some time BEFORE and AFTER the
# triggers so that filtering does not introduce artifacts into important parts.
trig_begin_experiment = bytes([1])
trig_end_experiment = bytes([16])

# Message when a new trial is started
trig_msg_new_trial = bytes([2])

# Wenever a new sample within a trial is started (fixation stim)
trig_sample_onset = bytes([3])

# Whenever a choice is being inquired during sampling
trig_left_choice = bytes([4])
trig_right_choice = bytes([5])
trig_final_choice = bytes([6])

# When displaying outcomes during sampling
trig_mask_outcome = bytes([7])
trig_outcome = bytes([8])

# Messaging when final choice is not possible because too few samples
trig_msg_zero_samples = bytes([9])

# Message when a final choice is started
trig_msg_final_choice = bytes([10])

# Whenever a final choice is started (fixation stim)
trig_choice_onset = bytes([11])

# Inquiring actions during CHOICE
trig_left_final_choice = bytes([12])
trig_right_final_choice = bytes([13])

# Displaying outcomes during CHOICE
trig_mask_final_outcome = bytes([14])
trig_final_outcome = bytes([15])
