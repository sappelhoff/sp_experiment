"""Functions to provide variable documentation."""
from sp_experiment.define_ttl_triggers import provide_trigger_dict


def make_events_json_dict():
    """Provide a dict to describe all collected variables."""
    # Get the trigger values
    trigger_dict = provide_trigger_dict()
    events_json_dict = dict()

    # Start populating the dict
    events_json_dict['onset'] = {
        'Description': 'onset of the event',
        'Units': 'seconds'
    }

    events_json_dict['duration'] = {
        'Description': 'duration of the event',
        'Units': 'seconds'
    }

    events_json_dict['trial'] = {
        'Description': ('zero indexed trial counter, where a trial is a '
                        'sequence of steps that ends with a final choice.')
    }

    events_json_dict['action_type'] = {
        'Description': ('type of the action that the subject performed at '
                        'this event within a trial',),
        'Levels': {
            'sample': ('the subject sampled either the left or the right '
                       'option'),
            'stop': ('the subject decided to stop sampling the options and '
                     'instead use the next action for a final choice'),
            'foced_stop': ('the subject took a maximum of samples and wanted '
                           'to take another one, so we force stopped in this '
                           'turn'),
            'premature_stop': ('the subject tried to stop sampling before '
                               'taking a single sample. This lead to an '
                               'error.'),
            'final_choice': ('the subject chose either the left or the right '
                             'option as a final choice')
        }
    }

    events_json_dict['action'] = {
        'Description': ('the concrete action that the subject performed for '
                        'the action type'),
        'Levels': {
            '0': 'the subject picked the *left* option',
            '1': 'the subject picked the *right* option',
            '2': ('the subject decided to stop sampling - for action_type '
                  '*stop* only')
        }
    }

    events_json_dict['outcome'] = {
        'Description': ('the outcome that the subject received for their '
                        'action. Numbers in the range 1 to 9.'),
    }

    events_json_dict['response_time'] = {
        'Description': ('the time it took the subject to respond after the '
                        'onset of the event'),
        'Units': 'milliseconds'
    }

    events_json_dict['value'] = {
        'Description': ('the TTL trigger value (=EEG marker value) '
                        'associated with an event'),
        'Levels': {
            trigger_dict['trig_begin_experiment']: ('beginning of the '
                                                    'experiment'),
            trigger_dict['trig_end_experiment']: ('end of the experiment'),
            trigger_dict['trig_new_trl']: ('color of fixcross is changed to '
                                           'indicate start of new trial'),
            trigger_dict['trig_sample_onset']: ('onset of new sample within '
                                                'a trial (fixcross changes '
                                                'to white color)'),
            trigger_dict['trig_left_choice']: ('subject chose *left* during '
                                               'sampling'),
            trigger_dict['trig_right_choice']: ('subject chose *right* '
                                                'during sampling'),
            trigger_dict['trig_final_choice']: ('subject chose *stop* during '
                                                'sampling'),
            trigger_dict['trig_mask_outcome']: ('a masked outcome is shown '
                                                'after sampling'),
            trigger_dict['trig_show_outcome']: ('a masked outcome is revealed '
                                                'after sampling'),
            trigger_dict['trig_new_final_choice']: ('color of fixcross is '
                                                    'changed to indicate '
                                                    'start of a final choice'),
            trigger_dict['trig_final_choice_onset']: ('onset of new final '
                                                      'choice at the end of '
                                                      'trial (fixcross '
                                                      'changes to white '
                                                      'color)'),
            trigger_dict['trig_left_final_choice']: ('subject chose *left* '
                                                     'for final choice'),
            trigger_dict['trig_right_final_choice']: ('subject chose *right* '
                                                      'for final choice'),
            trigger_dict['trig_mask_final_outcome']: ('a masked outcome is '
                                                      'shown after final '
                                                      'choice'),
            trigger_dict['trig_show_final_outcome']: ('a masked outcome is '
                                                      'revealed after final '
                                                      'choice'),
            trigger_dict['trig_error']: ('color of fixcross is changed to '
                                         'indicate an error (ignore all '
                                         'markers prior to this marker '
                                         'within this trial)'),
            trigger_dict['trig_forced_stop']: ('subject took the maximum '
                                               'number of samples and wanted '
                                               'to take yet another one'),
            trigger_dict['trig_premature_stop']: ('subject tried to make a '
                                                  'final choice before taking '
                                                  'at least one sample'),
            trigger_dict['trig_block_feedback']: ('block feedback is '
                                                  'displayed)')
        }
    }

    events_json_dict['mag0_1'] = {
        'LongName': 'magnitude 0_1',
        'Description': ('the first of two possible magnitudes in '
                        'outcomes for option 0')
    }

    events_json_dict['prob0_1'] = {
        'LongName': 'probability 0_1',
        'Description': ('the first of two possible probabilities in '
                        'outcomes for option 0')
    }

    events_json_dict['mag0_2'] = {
        'LongName': 'magnitude 0_2',
        'Description': ('the second of two possible magnitudes in '
                        'outcomes for option 0')
    }

    events_json_dict['prob0_2'] = {
        'LongName': 'probability 0_2',
        'Description': ('the second of two possible probabilities in '
                        'outcomes for option 0')
    }

    events_json_dict['mag1_1'] = {
        'LongName': 'magnitude 1_1',
        'Description': ('the first of two possible magnitudes in '
                        'outcomes for option 1')
    }

    events_json_dict['prob1_1'] = {
        'LongName': 'probability 1_1',
        'Description': ('the first of two possible probabilities in '
                        'outcomes for option 1')
    }

    events_json_dict['mag1_2'] = {
        'LongName': 'magnitude 1_2',
        'Description': ('the second of two possible magnitudes in '
                        'outcomes for option 1')
    }

    events_json_dict['prob1_2'] = {
        'LongName': 'probability 1_2',
        'Description': ('the second of two possible probabilities in '
                        'outcomes for option 1')
    }

    events_json_dict['version'] = {
        'Description': ('version of the experiment used for collecting this '
                        'data.')
    }

    events_json_dict['reset'] = {
        'Description': ('boolean that describes whether of not to ignore '
                        'events prior to this event in the current trial.'),
        'Levels': {
            '0': ('so far no error in this trial since the beginning or the '
                  'last error'),
            '1': ('error committed: disregard all events prior to this event '
                  'for the current trial.')
        }
    }

    # Keys in levels for "value" are bytes: we need to turn them into integers
    events_json_dict['value']['Levels'] = {ord(key): val for key, val in
                                           events_json_dict['value']['Levels'].items()}  # noqa: E501

    # return
    return events_json_dict
