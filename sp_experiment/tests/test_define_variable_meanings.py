"""Test the variable meanings dictionary."""
import os
import os.path as op
import json

import sp_experiment
from sp_experiment.define_variable_meanings import (make_description_task_json,
                                                    make_events_json_dict,
                                                    make_data_dir)


def test_make_events_json_dict():
    """Test the variable meanings."""
    events_json_dict = make_events_json_dict()
    assert isinstance(events_json_dict, dict)

    # The keys for "value levels" should be str of int
    for key in events_json_dict['value']['Levels'].keys():
        assert isinstance(key, int)
        assert key >= 0 and key <= 255

    # Also test descriptions task json
    events_json_dict = make_description_task_json()
    assert isinstance(events_json_dict, dict)


def test_json():
    """Test json file."""
    init_dir = op.dirname(sp_experiment.__file__)
    fname = 'task-sp_events.json'
    fpath = op.join(init_dir, 'experiment_data', fname)

    # In json does not exist, write it.
    if not op.exists(fpath):
        os.makedirs(op.join(init_dir, 'experiment_data'))
        events_json_dict = make_events_json_dict()
        with open(fpath, 'w') as fout:
            json.dump(obj=events_json_dict, fp=fout,
                      sort_keys=False, indent=4)

    # Load json and check for integrity
    with open(fpath, 'r') as fin:
        try:
            saved_json_dict = json.load(fin)
        except ValueError as e:
            print('invalid json: {}'.format(e))
            raise

    # Test that saved JSON is up to date
    events_json_dict = make_description_task_json()
    assert events_json_dict == saved_json_dict


def test_make_data_dir():
    """Test making of datadir and copying over of relevant files."""
    init_dir, data_dir = make_data_dir()
    assert op.exists(data_dir)
    assert op.exists(op.join(data_dir, 'task-sp_events.json'))
    assert op.exists(op.join(data_dir, 'sub-999_task-spactive_events.tsv'))
