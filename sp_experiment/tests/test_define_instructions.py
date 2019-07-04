"""Simple tests for the instructions that do not rely on psychopy."""
import os
import os.path as op

import sp_experiment
from sp_experiment.define_instructions import (provide_start_str,
                                               provide_stop_str,
                                               provide_blockfbk_str,
                                               print_human_readable_instrs)


def test_provide_start_str():
    """Test str provider."""
    s = provide_start_str(True, 'active', 'en')
    assert 'TEST for task A' in s
    s = provide_start_str(False, 'passive', 'de')
    assert 'der Aufgabe B' in s


def test_provide_stop_str():
    """Test str provider."""
    s = provide_stop_str(True, 'de')
    assert 'Die TEST Aufgabe' in s
    s = provide_stop_str(False, 'en')
    assert 'The task is over' in s


def test_provide_blockfdb_str():
    """Test str provider."""
    data_file = op.join(op.dirname(sp_experiment.__file__), 'tests', 'data',
                        'sub-999_task-spactive_events.tsv')
    s = provide_blockfbk_str(data_file, 1, 1, 'en')
    assert 'Block 1/1 done' in s

    s = provide_blockfbk_str(data_file, 1, 1, 'de')
    assert 'Block 1/1 beendet' in s


def test_print_human_readable_instrs():
    """Test printing the instructions, and actually do so."""
    init_dir = op.dirname(sp_experiment.__file__)
    root_dir = op.abspath(op.join(init_dir, '..'))
    instr_dir = op.join(root_dir, 'instructions')
    # If not existing, make a fresh one
    if not op.exists(instr_dir):
        os.makedirs(instr_dir)
    # Write the instructions, auto-overwriting old ones
    for kind in ['general', 'active', 'passive', 'description']:
        fpath = op.join(instr_dir, 'instructions_{}.txt'.format(kind))
        print_human_readable_instrs(kind, fpath)
