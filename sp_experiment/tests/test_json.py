"""Test the json file with keys and values describing the data file."""
import os.path as op
import json

import sp_experiment


init_dir = op.dirname(sp_experiment.__file__)
fname = 'task-sp_events.json'
fpath = op.join(init_dir, fname)


def test_json():
    """Test json file."""
    with open(fpath, 'r') as f:
        try:
            assert json.load(f)
        except ValueError as e:
            print('invalid json: %s' % e)
            raise
