"""Definitions for the TTL triggers to be sent.

main file: sp.py

For more information, see also the "event_value" key within the
"task-sp_events.json" file.

"""

# At the beginning and end of the experiment ... take these triggers to crop
# the meaningful EEG data. Make sure to include some time BEFORE and AFTER the
# triggers so that filtering does not introduce artifacts into important parts.
trig_begin_experiment = bytes([1])
trig_end_experiment = bytes([2])

# Indication when a new trial is started
trig_new_trl = bytes([3])

# Wenever a new sample within a trial is started (fixation stim)
trig_sample_onset = bytes([4])

# Whenever a choice is being inquired during sampling
trig_left_choice = bytes([5])
trig_right_choice = bytes([6])
trig_final_choice = bytes([7])

# When displaying outcomes during sampling
trig_mask_outcome = bytes([8])
trig_show_outcome = bytes([9])

# Indication when a final choice is started
trig_new_final_choice = bytes([10])

# Whenever a final choice is started (fixation stim)
trig_final_choice_onset = bytes([11])

# Inquiring actions during CHOICE
trig_left_final_choice = bytes([12])
trig_right_final_choice = bytes([13])

# Displaying outcomes during CHOICE
trig_mask_final_outcome = bytes([14])
trig_show_final_outcome = bytes([15])

# trigger for ERROR, when a trial has to be reset
# (ignore all markers prior to this marker within this trial)
trig_error = bytes([16])

# If the subject sampled a maximum of steps and now wants to take yet another
# one, we force stop and initiate a final choice
trig_forced_stop = bytes([17])

# If subject tried to make a final choice before taking at least one sample
trig_premature_stop = bytes([18])
