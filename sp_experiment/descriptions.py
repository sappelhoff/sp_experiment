"""Inquire participant's decisions from descriptions.

Based on a data file collected in the active SP condition, provide gambles
from descriptions.
"""
import os
import os.path as op

import pandas as pd
from psychopy import visual, event, core

import sp_experiment
from sp_experiment.define_variable_meanings import make_description_task_json
from sp_experiment.define_instructions import instruct_str_descriptions
from sp_experiment.utils import _get_payoff_setting, KEYLIST_DESCRIPTION


def run_descriptions(events_file, monitor='testMonitor', font='', lang='en'):
    """Run decisions from descriptions.

    Parameters
    ----------
    events_file : str
        Path to sub-{id:02d}_task-spactive_events.tsv file for
        a given subject id.

    Returns
    -------
    data_file : str
        Path to the output data file

    """
    # Define monitor specific window object
    win = visual.Window(color=(0, 0, 0),  # Background color: RGB [-1,1]
                        fullscr=True,  # Fullscreen for better timing
                        monitor=monitor,
                        winType='pyglet')

    # Hide the cursor
    win.mouseVisible = False

    # prepare text object
    txt_color = (0.45, 0.45, 0.45)
    txt_stim = visual.TextStim(win,
                               color=txt_color,
                               units='deg',
                               pos=(-0.5, 0))
    txt_stim.height = 1
    txt_stim.font = font

    # Start a clock for measuring reaction times
    # NOTE: Will be reset to 0 right before recording a button press
    rt_clock = core.Clock()

    # Start a clock for general experiment time
    exp_timer = core.MonotonicClock()

    # Print some instructions
    txt_stim.text = instruct_str_descriptions(lang)
    txt_stim.draw()
    win.flip()
    event.waitKeys()

    # prepare logging and read in present data
    df = pd.read_csv(events_file, sep='\t')
    head, tail = op.split(events_file)
    sub_part = tail.split('_task')[0]
    fname = sub_part + '_task-description_events.tsv'
    data_file = op.join(head, fname)

    variable_meanings_dict = make_description_task_json()
    variables = list(variable_meanings_dict.keys())
    with open(data_file, 'w') as fout:
        header = '\t'.join(variables)
        fout.write(header + '\n')

    # Now collect the data
    ntrials = int(df['trial'].max())+1
    for trial in range(ntrials):
        setting = _get_payoff_setting(df, trial)
        setting[0, [2, 3, 6, 7]] *= 10  # multiply probs to be in percent
        setting = setting.astype(int)

        mag0_1 = setting[0, 0]
        prob0_1 = setting[0, 2] * 10
        mag0_2 = setting[0, 1]
        prob0_2 = setting[0, 3] * 10
        mag1_1 = setting[0, 4]
        prob1_1 = setting[0, 6] * 10
        mag1_2 = setting[0, 5]
        prob1_2 = setting[0, 7] * 10
        txt_stim.text = (f'{mag0_1} - {prob0_1}%    |    '  # noqa: E999
                         f'{mag1_1} - {prob1_1}%\n'
                         f'{mag0_2} - {prob0_2}%    |    '
                         f'{mag1_2} - {prob1_2}%')
        txt_stim.draw()
        rt_clock.reset()
        onset = exp_timer.getTime()
        win.flip()
        # Collect response
        keys_rts = event.waitKeys(maxWait=float('inf'),
                                  keyList=KEYLIST_DESCRIPTION,
                                  timeStamped=rt_clock)
        key, rt = keys_rts[0]
        if key == 'x':
            win.close()
            core.quit()

        side = KEYLIST_DESCRIPTION.index(key)
        with open(data_file, 'a') as fout:
            values = [onset, rt, trial, side]
            values = [str(val) for val in values]
            fout.write('\t'.join(values))

    return data_file


if __name__ == '__main__':
    init_dir = op.dirname(sp_experiment.__file__)
    fname = 'sub-999_task-spactive_events.tsv'
    fpath = op.join(init_dir, 'tests', 'data', fname)
    data_file = run_descriptions(fpath)
    os.remove(data_file)
