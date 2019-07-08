"""Definitions for the TTL triggers to be sent.

main file: sp.py

For more information, see also the "event_value" key within the
define_variable_meanings.make_events_json_dict.

"""
from collections import OrderedDict


def provide_trigger_dict():
    """Provide a dictionnary mapping str names to byte values."""
    trigger_dict = OrderedDict()

    # At the beginning and end of the experiment ... take these triggers to
    # crop the meaningful EEG data. Make sure to include some time BEFORE and
    # AFTER the triggers so that filtering does not introduce artifacts into
    # important parts.
    trigger_dict['trig_begin_experiment'] = bytes([1])
    trigger_dict['trig_end_experiment'] = bytes([2])

    # Indication when a new trial is started
    trigger_dict['trig_new_trl'] = bytes([3])

    # Wenever a new sample within a trial is started (fixation stim)
    trigger_dict['trig_sample_onset'] = bytes([4])

    # Whenever a choice is being inquired during sampling
    trigger_dict['trig_left_choice'] = bytes([5])
    trigger_dict['trig_right_choice'] = bytes([6])
    trigger_dict['trig_final_choice'] = bytes([7])

    # When displaying outcomes during sampling
    trigger_dict['trig_mask_out_l'] = bytes([8])
    trigger_dict['trig_show_out_l'] = bytes([9])
    trigger_dict['trig_mask_out_r'] = bytes([10])
    trigger_dict['trig_show_out_r'] = bytes([11])

    # Indication when a final choice is started
    trigger_dict['trig_new_final_choice'] = bytes([12])

    # Whenever a final choice is started (fixation stim)
    trigger_dict['trig_final_choice_onset'] = bytes([13])

    # Inquiring actions during CHOICE
    trigger_dict['trig_left_final_choice'] = bytes([14])
    trigger_dict['trig_right_final_choice'] = bytes([15])

    # Displaying outcomes during CHOICE
    trigger_dict['trig_mask_final_out_l'] = bytes([16])
    trigger_dict['trig_show_final_out_l'] = bytes([17])
    trigger_dict['trig_mask_final_out_r'] = bytes([18])
    trigger_dict['trig_show_final_out_r'] = bytes([19])

    # trigger for ERROR, when a trial has to be reset
    # (ignore all markers prior to this marker within this trial)
    trigger_dict['trig_error'] = bytes([20])

    # If the subject sampled a maximum of steps and now wants to take yet
    # another one, we force stop and initiate a final choice
    trigger_dict['trig_forced_stop'] = bytes([21])

    # If subject tried to make a final choice before taking at least one sample
    trigger_dict['trig_premature_stop'] = bytes([22])

    # Display the block feedback
    trigger_dict['trig_block_feedback'] = bytes([23])

    return trigger_dict


if __name__ == '__main__':
    import serial
    from time import sleep
    from sp_experiment.utils import My_serial
    ser = serial.Serial('COM4')
    ser = My_serial(ser, waittime=0.005)
    trigger_dict = provide_trigger_dict()

    for key, val in trigger_dict.items():
        print('{}: {}'.format(ord(val), key))
        ser.write(val)
        sleep(1.5)
