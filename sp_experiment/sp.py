"""Implement the experimental flow of the sampling paradigm.

Version information
-------------------
0.1.0-dev: Experiment with fixed horizon, basically the "final choice" key
           is not part of the accepted keys anymore and the maximum number of
           samples is set to the fixed horizon. Participants then sample and
           upon reaching the horizon and attempting to take one more sample,
           they are informed that the next sample will be a final choice.
0.1.0: The experiment with an open horizon

To do
-----
- incorporate eye tracking (gaze-contingent fixation cross)

"""
import os
import os.path as op

import numpy as np
import pandas as pd
from psychopy import visual, event, core, gui

from sp_experiment.define_variable_meanings import (make_events_json_dict,
                                                    make_data_dir
                                                    )
from sp_experiment.utils import (KEYLIST_SAMPLES,
                                 KEYLIST_FINCHOICE,
                                 UTILS_FPS,
                                 get_fixation_stim,
                                 calc_bonus_payoff,
                                 set_fixstim_color,
                                 get_jittered_waitframes,
                                 log_data,
                                 Fake_serial,
                                 get_payoff_dict,
                                 get_passive_action,
                                 get_passive_outcome,
                                 get_final_choice_outcomes
                                 )
from sp_experiment.define_payoff_settings import (get_payoff_settings,
                                                  get_random_payoff_dict,
                                                  )
from sp_experiment.define_ttl_triggers import provide_trigger_dict


def navigation():
    """Lead through a navigation GUI.

    Provides the options to run the experiment, test trials, or print out the
    bonus money of a participant. If 'run' is selected, it returns True. Else
    it either starts the test trials and quits, or prints the bonus money and
    quits.

    Returns
    -------
    run : bool

    """
    run = False
    nav = 'initial'
    bonus = ''
    while not nav == 'finished':
        # Prepare GUI
        myDlg = gui.Dlg(title='Sampling Paradigm Experiment')
        if nav == 'initial':
            myDlg.addField('What to do?:', choices=['run experiment',
                                                    'run test trials',
                                                    'calculate bonus money'])
        elif nav == 'testing_cond':
            myDlg.addField('Condition:', choices=['active', 'passive'])

        elif nav == 'calc_bonus':
            myDlg.addField('ID:', choices=list(range(1, 21)))

        elif nav == 'show_bonus':
            myDlg.addFixedField('Bonus:', bonus)
            nav = 'quit'

        # Get data
        ok_data = myDlg.show()
        if myDlg.OK:
            if ok_data[0] == 'run experiment':
                print('running experiment now')
                run = True
                nav = 'finished'  # quit navigattion and run experiment
            elif ok_data[0] == 'run test trials':
                nav = 'testing_cond'
            elif nav == 'testing_cond':
                print('preparing test trials now')
                # run test trials, then quit program
                run_test_trials(condition=ok_data[0])
                core.quit()
            elif ok_data[0] == 'calculate bonus money':
                nav = 'calc_bonus'  # ask for ID
            elif nav == 'calc_bonus':
                bonus = calc_bonus_payoff(int(ok_data[0]))
                nav = 'show_bonus'
            elif nav == 'quit':
                core.quit()  # We have shown the bonus. Now quit program
        else:
            print('user cancelled GUI input')
            core.quit()

    return run


def prep_logging(yoke_map):
    """Prepare logging for the experiment run.

    Parameters
    ----------
    yoke_map : dict
        dictionary mapping a sub_id to a previous sub_id that performed the
        active task. That task will then be served as a replay to the current
        ID.

    Returns
    -------
    data_file : str
        path to the data file

    """
    # Collect the ID, age, sex, condition
    myDlg = gui.Dlg(title='Sampling Paradigm Experiment')
    myDlg.addField('ID:', choices=list(range(1, 21)))
    myDlg.addField('Age:', choices=list(range(18, 100)))
    myDlg.addField('Sex:', choices=['Male', 'Female'])
    myDlg.addField('Condition:', choices=['active', 'passive'])

    # show dialog and wait for OK or Cancel
    ok_data = myDlg.show()
    if myDlg.OK:  # or if ok_data is not None
        sub_id = int(ok_data[0])
        age = int(ok_data[1])
        sex = ok_data[2]
        condition = ok_data[3]
        yoke_to = yoke_map[sub_id]
    else:
        print('user cancelled GUI input')
        core.quit()

    # Data logging
    # ============
    fname = f'sub-{sub_id:02d}_task-sp{condition}_events.tsv'  # noqa: E999

    # Check directory is present and file name not yet used
    init_dir, data_dir = make_data_dir()

    data_file = op.join(data_dir, fname)
    if op.exists(data_file):
        raise OSError(f'A data file for {sub_id} '
                      f'already exists: {data_file}')

    # Write header to the tab separated log file
    variable_meanings_dict = make_events_json_dict()
    variables = list(variable_meanings_dict.keys())

    with open(data_file, 'w') as fout:
        header = '\t'.join(variables)
        fout.write(header + '\n')

    # Write a brief log file for this participant
    fname = f'log_{sub_id}_{condition}.txt'
    log_path = op.join(data_dir, fname)
    with open(log_path, 'w') as fout:
        for line in [sub_id, age, sex, condition, yoke_to]:
            fout.write(f'{line}')  # noqa E999
            fout.write('\n')

    return data_file, condition, yoke_to


def run_flow(monitor='testMonitor', ser=Fake_serial(), max_ntrls=10,
             max_nsamples=12, block_size=10, data_file=None,
             condition='active', yoke_to=None, is_test=False):
    """Run the experimental flow.

    Parameters
    ----------
    monitor : str
        Monitor definitionto be used, see define_monitors.py
    ser : str | instance of Fake_serial. Defaults to None.
        Either string address to a serial port for sending triggers, or
        a Fake_serial object, see utils.py. Defaults to Fake_serial.
    max_ntrls : int
        Maximum number of trials for this run.
    max_nsamples : int
        Maximum number of samples per trial.
    block_size : int
        Number of trials after which feedback is provided
    data_file : str | None
        Path to the data file
    condition : str
        Condition in which to run the experiment
    yoke_to : int | None
        sub_id which to yoke a subject to in passive condition.
    is_test : bool
        Flag whether this is a test run.

    """
    if data_file is None:
        raise ValueError('Please provide a data_file path.')

    # Get PsychoPy stimuli ready
    # ==========================
    # Define monitor specific window object
    win = visual.Window(color=(0, 0, 0),  # Background color: RGB [-1,1]
                        fullscr=True,  # Fullscreen for better timing
                        monitor=monitor,
                        units='deg',
                        winType='pyglet')

    # Hide the cursor
    win.mouseVisible = False

    # On which frame rate are we operating?
    fps = int(round(win.getActualFrameRate()))
    assert fps == 60
    if UTILS_FPS != fps:
        raise ValueError('Please adjust the UTILS_FPS variable in utils.py')

    # Mask and text for outcomes, properties will be set and reset below
    circ_color = (-0.45, -0.45, -0.45)
    circ_stim = visual.Circle(win,
                              pos=(0, 0),
                              units='deg',
                              fillColor=circ_color,
                              lineColor=circ_color,
                              radius=2.5,
                              edges=128)

    txt_color = (0.45, 0.45, 0.45)
    txt_stim = visual.TextStim(win,
                               units='deg',
                               color=txt_color)

    # Get the objects for the fixation stim
    outer, inner, horz, vert = get_fixation_stim(win, stim_color=txt_color)
    fixation_stim_parts = [outer, horz, vert, inner]

    # Start communicating with the serial port
    # ========================================
    if isinstance(ser, Fake_serial):
        pass

    # Trigger meanings and values
    trigger_dict = provide_trigger_dict()

    # Experiment settings
    # ===================
    # Make sure block settings are fine
    assert max_ntrls % block_size == 0
    nblocks = int(max_ntrls/block_size)

    font = 'Liberation Sans'  # Looks like Arial, but it's free!

    tfeeddelay_ms = (200, 400)  # time for delaying feedback after an action
    toutmask_ms = (800, 800)  # time for masking an outcome ("show blob")
    toutshow_ms = (500, 500)  # time for showing an outcome ("show number")
    tdisplay_ms = (1000, 1000)  # show color: new trial, error, final choice

    maxwait_samples = 3  # Maximum seconds we wait for a sample
    maxwait_finchoice = 3  # can also be float('inf') to wait forever

    expected_value_diff = 0.1  # For payoff settings to be used

    # Set the fixation_stim colors for signalling state of the experiment
    color_standard = txt_color  # prompt for an action
    color_newtrl = (0, 1, 0)  # wait: a new trial is starting
    color_finchoice = (0, 0, 1)  # wait: next action will be "final choice"
    color_error = (1, 0, 0)  # wait: you did an error ... we have to restart

    # Start the experimental flow
    # ===========================
    # Get ready to start the experiment. Start timing from next button press.
    modstr = 'experiment' if not is_test else 'TEST TRIAL'
    txt_stim.text = (f'Starting the {modstr} in {condition} condition! '
                     'Press any key to start.')
    txt_stim.height = 1
    txt_stim.font = font
    txt_stim.draw()
    win.flip()
    event.waitKeys()
    ser.write(trigger_dict['trig_begin_experiment'])
    exp_timer = core.MonotonicClock()
    log_data(data_file, onset=exp_timer.getTime(),
             value=trigger_dict['trig_begin_experiment'])
    txt_stim.height = 4  # set height for stimuli to be shown below

    # Get general payoff settings
    payoff_settings = get_payoff_settings(expected_value_diff)

    # Start a clock for measuring reaction times
    # NOTE: Will be reset to 0 right before recording a button press
    rt_clock = core.Clock()

    # If we are in the passive condition, load pre-recorded data to replay
    if condition == 'passive':
        fname = f'sub-{yoke_to}_task-spactive_events.tsv'
        fpath = op.join(op.dirname(data_file), fname)
        df = pd.read_csv(fpath, sep='\t')
        df = df[pd.notnull(df['trial'])]

    current_nblocks = 0
    current_ntrls = 0
    while current_ntrls < max_ntrls:

        # For each trial, take a new payoff setting.
        # When active condition, read current data to make pseudorandom draw
        # of a payoff setting. This is to guarantee that also stimuli that have
        # been sampled the least so far will be included more often.
        if condition == 'active':
            df_pseudorand = pd.read_csv(data_file, sep='\t')
            (payoff_dict,
             payoff_settings) = get_random_payoff_dict(payoff_settings,
                                                       pseudorand=True,
                                                       df=df_pseudorand
                                                       )

            log_data(data_file, onset=exp_timer.getTime(), trial=current_ntrls,
                     payoff_dict=payoff_dict)
        else:  # condition == 'passive'
            payoff_dict = get_payoff_dict(df, current_ntrls)
            log_data(data_file, onset=exp_timer.getTime(), trial=current_ntrls,
                     payoff_dict=payoff_dict)

        # Starting a new trial
        [stim.setAutoDraw(True) for stim in fixation_stim_parts]
        set_fixstim_color(inner, color_newtrl)
        win.callOnFlip(ser.write, trigger_dict['trig_new_trl'])
        frames = get_jittered_waitframes(*tdisplay_ms)
        for frame in range(frames):
            win.flip()
            if frame == 0:
                log_data(data_file, onset=exp_timer.getTime(),
                         trial=current_ntrls,
                         value=trigger_dict['trig_new_trl'], duration=frames)

        # Within this trial, allow sampling
        current_nsamples = 0
        while True:
            # Starting a new sample by setting the fix stim to standard color
            set_fixstim_color(inner, color_standard)
            win.callOnFlip(ser.write, trigger_dict['trig_sample_onset'])
            win.flip()
            rt_clock.reset()
            log_data(data_file, onset=exp_timer.getTime(), trial=current_ntrls,
                     value=trigger_dict['trig_sample_onset'])

            if condition == 'active':
                # Wait for an action of the participant
                keys_rts = event.waitKeys(maxWait=maxwait_samples,
                                          keyList=KEYLIST_SAMPLES,
                                          timeStamped=rt_clock)
            else:  # condition == 'passive'
                # Load action from recorded data
                keys_rts = get_passive_action(df, current_ntrls,
                                              current_nsamples)
                rt = keys_rts[0][-1]
                # safeguard to never wait for more than maxwait_samples secs,
                # which is otherwise possible in the first sample of a trial
                if rt >= maxwait_samples:
                    rt = np.random.randint(0, maxwait_samples)
                core.wait(rt)  # wait for the time that was the RT

            if not keys_rts:
                if current_nsamples == 0:
                    # No keypress in due time: Is this the first sample in the
                    # trial? If yes, forgive them and wait for a response
                    # forever
                    keys_rts = event.waitKeys(maxWait=float('inf'),
                                              keyList=KEYLIST_SAMPLES,
                                              timeStamped=rt_clock)
                else:  # Else: raise an error and start new trial
                    set_fixstim_color(inner, color_error)
                    win.callOnFlip(ser.write, trigger_dict['trig_error'])
                    frames = get_jittered_waitframes(*tdisplay_ms)
                    for frame in range(frames):
                        win.flip()
                        if frame == 0:
                            # Log an event that we have to disregard all prior
                            # events in this trial
                            log_data(data_file, onset=exp_timer.getTime(),
                                     trial=current_ntrls,
                                     value=trigger_dict['trig_error'],
                                     duration=frames, reset=True)
                    # start a new trial without incrementing the trial counter
                    break

            # Send trigger
            key, rt = keys_rts[0]
            current_nsamples += 1
            action = KEYLIST_SAMPLES.index(key)
            if action == 0 and current_nsamples <= max_nsamples:
                ser.write(trigger_dict['trig_left_choice'])
                value = trigger_dict['trig_left_choice']
            elif action == 1 and current_nsamples <= max_nsamples:
                ser.write(trigger_dict['trig_right_choice'])
                value = trigger_dict['trig_right_choice']
            elif action == 2 and current_nsamples > 1:
                ser.write(trigger_dict['trig_final_choice'])
                value = trigger_dict['trig_final_choice']
            elif action in [0, 1] and current_nsamples > max_nsamples:
                # sampling too much, final choice is being forced
                ser.write(trigger_dict['trig_forced_stop'])
                value = trigger_dict['trig_forced_stop']
                action = 5 if action == 0 else 6
            elif action == 2 and current_nsamples <= 1:
                # premature final choice. will lead to error
                ser.write(trigger_dict['trig_premature_stop'])
                value = trigger_dict['trig_premature_stop']
                action = 7
            elif action == 3:
                core.quit()

            log_data(data_file, onset=exp_timer.getTime(), trial=current_ntrls,
                     action=action, response_time=rt, value=value)

            # Proceed depending on action
            if action in [0, 1] and current_nsamples <= max_nsamples:
                # Display the outcome
                if condition == 'active':
                    outcome = np.random.choice(payoff_dict[action])
                else:  # condition == 'passive'
                    # note: deduct one off current_nsamples because we already
                    # added one (see above) which is to early for this line of
                    # code
                    outcome = get_passive_outcome(df, current_ntrls,
                                                  current_nsamples-1)
                pos = (-5, 0) if action == 0 else (5, 0)
                circ_stim.pos = pos
                txt_stim.pos = pos
                txt_stim.text = str(outcome)
                # manually push text to center of circle
                txt_stim.pos += (0, 0.3)

                # delay feedback
                frames = get_jittered_waitframes(*tfeeddelay_ms)
                for frame in range(frames):
                    win.flip()

                win.callOnFlip(ser.write, trigger_dict['trig_mask_outcome'])
                frames = get_jittered_waitframes(*toutmask_ms)
                for frame in range(frames):
                    circ_stim.draw()
                    win.flip()
                    if frame == 0:
                        log_data(data_file, onset=exp_timer.getTime(),
                                 trial=current_ntrls, duration=frames,
                                 value=trigger_dict['trig_mask_outcome'])

                win.callOnFlip(ser.write, trigger_dict['trig_show_outcome'])
                frames = get_jittered_waitframes(*toutshow_ms)
                for frame in range(frames):
                    circ_stim.draw()
                    txt_stim.draw()
                    win.flip()
                    if frame == 0:
                        log_data(data_file, onset=exp_timer.getTime(),
                                 trial=current_ntrls, duration=frames,
                                 outcome=outcome,
                                 value=trigger_dict['trig_show_outcome'])

            else:  # action == 2 or current_nsamples > max_nsamples
                # First need to check that a minimum of samples has been taken
                # otherwise, it's an error
                if current_nsamples <= 1:
                    set_fixstim_color(inner, color_error)
                    win.callOnFlip(ser.write, trigger_dict['trig_error'])
                    frames = get_jittered_waitframes(*tdisplay_ms)
                    for frame in range(frames):
                        win.flip()
                        if frame == 0:
                            # Log an event that we have to disregard all prior
                            # events in this trial
                            log_data(data_file, onset=exp_timer.getTime(),
                                     trial=current_ntrls,
                                     value=trigger_dict['trig_error'],
                                     duration=frames, reset=True)
                    if condition == 'active':
                        # start a new trial without incrementing the trial
                        # counter
                        break
                    else:  # condition == 'passive'
                        # if a premature stop happens in passive condition, we
                        # need to drop if from the df in order not to enter an
                        # endless loop
                        # # NOTE: We also drop all trials previous to this one.
                        # They have been replayed, so it should be fine.
                        df = df[df['trial'] >= current_ntrls]
                        # drop rows before and including the *first*
                        # encountered premature stop ... also drop first
                        # following event which indicates the error coloring of
                        # the fixation stim ... retain all other events
                        mask = np.ones(df.shape[0])
                        i = np.where(df['action_type'] ==
                                     'premature_stop')[0][0]
                        mask[:i+2] = 0
                        mask = (mask == 1)
                        df = df[mask]
                        break
                # We survived the minimum samples check ...
                # Now get ready for final choice
                set_fixstim_color(inner, color_finchoice)
                win.callOnFlip(ser.write,
                               trigger_dict['trig_new_final_choice'])
                frames = get_jittered_waitframes(*tdisplay_ms)
                for frame in range(frames):
                    win.flip()
                    if frame == 0:
                        log_data(data_file, onset=exp_timer.getTime(),
                                 trial=current_ntrls,
                                 value=trigger_dict['trig_new_final_choice'],
                                 duration=frames)

                # Switch color of stim cross back to standard: action allowed
                set_fixstim_color(inner, color_standard)
                win.callOnFlip(ser.write,
                               trigger_dict['trig_final_choice_onset'])
                win.flip()
                rt_clock.reset()
                log_data(data_file, onset=exp_timer.getTime(),
                         trial=current_ntrls,
                         value=trigger_dict['trig_final_choice_onset'])

                # Wait for an action of the participant
                keys_rts = event.waitKeys(maxWait=maxwait_finchoice,
                                          keyList=KEYLIST_FINCHOICE,
                                          timeStamped=rt_clock)

                if not keys_rts:
                    # No keypress in due time: raise an error and start new
                    # trial
                    set_fixstim_color(inner, color_error)
                    win.callOnFlip(ser.write, trigger_dict['trig_error'])
                    frames = get_jittered_waitframes(*tdisplay_ms)
                    for frame in range(frames):
                        win.flip()
                        if frame == 0:
                            # Log an event that we have to disregard all prior
                            # events in this trial
                            log_data(data_file, onset=exp_timer.getTime(),
                                     trial=current_ntrls,
                                     value=trigger_dict['trig_error'],
                                     duration=frames, reset=True)
                    # start a new trial without incrementing the trial counter
                    break

                key, rt = keys_rts[0]
                action = KEYLIST_FINCHOICE.index(key)
                if action == 0:
                    ser.write(trigger_dict['trig_left_final_choice'])
                    value = trigger_dict['trig_left_final_choice']
                elif action == 1:
                    ser.write(trigger_dict['trig_right_final_choice'])
                    value = trigger_dict['trig_right_final_choice']
                elif action == 2:
                    core.quit()

                # NOTE: add 3 to "action" to distinguish final choice from
                # sampling
                log_data(data_file, onset=exp_timer.getTime(),
                         trial=current_ntrls, action=action+3,
                         response_time=rt, value=value)
                current_nsamples += 1

                # Display final outcome
                outcome = np.random.choice(payoff_dict[action])
                pos = (-5, 0) if action == 0 else (5, 0)
                circ_stim.pos = pos
                txt_stim.pos = pos
                txt_stim.text = str(outcome)
                # manually push text to center of circle
                txt_stim.pos += (0, 0.3)
                txt_stim.color = (0, 1, 0)

                # delay feedback
                frames = get_jittered_waitframes(*tfeeddelay_ms)
                for frame in range(frames):
                    win.flip()

                win.callOnFlip(ser.write,
                               trigger_dict['trig_mask_final_outcome'])
                frames = get_jittered_waitframes(*toutmask_ms)
                for frame in range(frames):
                    circ_stim.draw()
                    win.flip()
                    if frame == 0:
                        log_data(data_file, onset=exp_timer.getTime(),
                                 trial=current_ntrls, duration=frames,
                                 value=trigger_dict['trig_mask_final_outcome'])

                win.callOnFlip(ser.write,
                               trigger_dict['trig_show_final_outcome'])
                frames = get_jittered_waitframes(*toutshow_ms)
                for frame in range(frames):
                    circ_stim.draw()
                    txt_stim.draw()
                    win.flip()
                    if frame == 0:
                        log_data(data_file, onset=exp_timer.getTime(),
                                 trial=current_ntrls, duration=frames,
                                 outcome=outcome,
                                 value=trigger_dict['trig_show_final_outcome'])

                # Reset txt_color
                txt_stim.color = txt_color

                # Is a block finished? If yes, display block feedback and
                # provide a short break
                if (current_ntrls+1) % block_size == 0:
                    current_nblocks += 1

                    df_tmp = pd.read_csv(data_file, sep='\t')
                    outcomes = get_final_choice_outcomes(df_tmp)
                    points = int(np.sum(outcomes))
                    [stim.setAutoDraw(False) for stim in fixation_stim_parts]
                    txt_stim.text = (f'Block {current_nblocks}/{nblocks} done!'
                                     f' You earned {points} points so far.'
                                     ' Remember that your points will be '
                                     ' converted to Euros and paid to you at'
                                     ' the end of the experiment as a bonus.'
                                     ' Take a short break now.'
                                     ' Then press any key to continue.')
                    txt_stim.pos = (0, 0)
                    txt_stim.height = 1
                    txt_stim.draw()
                    win.callOnFlip(ser.write,
                                   trigger_dict['trig_block_feedback'])
                    win.flip()
                    log_data(data_file, onset=exp_timer.getTime(),
                             value=trigger_dict['trig_block_feedback'])
                    core.wait(1)  # wait for a bit so that this is not skipped
                    event.waitKeys()

                    # Reset stim settings for next block
                    [stim.setAutoDraw(True) for stim in fixation_stim_parts]
                    # set height for stimuli to be shown below
                    txt_stim.height = 4

                # start the next trial
                current_ntrls += 1
                break

    # We are done
    [stim.setAutoDraw(False) for stim in fixation_stim_parts]
    txt_stim.text = 'This task is over. Press any key to quit.'
    txt_stim.pos = (0, 0)
    txt_stim.height = 1

    txt_stim.draw()
    win.callOnFlip(ser.write, trigger_dict['trig_end_experiment'])
    win.flip()
    log_data(data_file, onset=exp_timer.getTime(),
             value=trigger_dict['trig_end_experiment'])
    event.waitKeys()
    win.close()


def run_test_trials(monitor='testMonitor', condition='active'):
    """Run the test trials.

    Parameters
    ----------
    monitor : str
        Name of the monitor to be used

    condition : str
        Condition for which to perform test trial. Can be 'active' or 'passive'

    """
    init_dir, data_dir = make_data_dir()
    data_file = op.join(data_dir, 'test'+str(hash(os.times())))

    # Write header to the tab separated log file
    variable_meanings_dict = make_events_json_dict()
    variables = list(variable_meanings_dict.keys())

    with open(data_file, 'w') as fout:
        header = '\t'.join(variables)
        fout.write(header + '\n')

    if condition == 'active':
        # Run a single active test trial
        run_flow(monitor=monitor,
                 max_ntrls=1,
                 max_nsamples=12,
                 block_size=1,  # i.e., no block feedback because never reached
                 data_file=data_file,
                 condition='active',
                 is_test=True)

    elif condition == 'passive':
        # Run a single passive test trial ... using a prerecorded dataset
        run_flow(monitor=monitor,
                 max_ntrls=1,
                 max_nsamples=12,
                 block_size=1,  # i.e., no block feedback because never reached
                 data_file=data_file,
                 condition='passive',
                 yoke_to=999,
                 is_test=True)

    # Remove the test data
    os.remove(data_file)


if __name__ == '__main__':
    # Yoking map
    # ==========
    # To determine, which participant gets yoked to which.
    # First 10 subjs are mapped to themselves
    yoke_map = dict(zip(list(range(1, 11)), list(range(1, 11))))
    # Next 10 are mapped to first ten
    for i, j in zip(list(range(11, 21)), list(range(1, 11))):
        yoke_map[i] = j

    # Navigate
    run = navigation()
    if run:
        data_file, condition, yoke_to = prep_logging(yoke_map)
        run_flow(monitor='eizoforis',
                 ser=Fake_serial(),
                 max_ntrls=75,
                 max_nsamples=12,
                 block_size=25,
                 data_file=data_file,
                 condition=condition,
                 yoke_to=yoke_to)

    core.quit()
