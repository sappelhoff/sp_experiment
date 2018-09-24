"""Definitions for the TTL triggers to be sent."""

# At the beginning and end of the experiment ... take these triggers to crop
# the meaningful EEG data. Make sure to include some time BEFORE and AFTER the
# triggers so that filtering does not introduce artifacts into important parts.
trig_begin_experiment = bytes([1])
trig_end_experiment = bytes([14])

# Message when a new trial is started
trig_msg_new_trial = bytes([2])

# Wenever a new sample within a trial is started (fixation stim)
trig_sample_onset = bytes([15])

# Whenever a choice is being inquired during sampling
trig_left_choice = bytes([3])
trig_right_choice = bytes([4])
trig_final_choice = bytes([5])

# When displaying outcomes during sampling
trig_mask_outcome = bytes([6])
trig_outcome = bytes([7])

# Messaging when final choice is not possible because too few samples
trig_msg_zero_samples = bytes([8])

# Message when a final choice is started
trig_msg_final_choice = bytes([9])

# Whenever a final choice is started (fixation stim)
trig_choice_onset = bytes([16])

# Inquiring actions during CHOICE
trig_left_final_choice = bytes([10])
trig_right_final_choice = bytes([11])
trig_mask_final_outcome = bytes([12])

# Displaying outcomes during CHOICE
trig_final_outcome = bytes([13])
