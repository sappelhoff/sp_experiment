"""Functions that either provide an instruction flow or a string to display."""
import os.path as op

import numpy as np
import pandas as pd

import sp_experiment
from sp_experiment.utils import get_final_choice_outcomes


def run_instructions(kind, monitor='testMonitor', font='', lang='em'):
    """Show experiment instructions on the screen.

    Parameters
    ----------
    kind : str
        Can be 'general', 'active', and 'passive'.

    """
    from psychopy import visual, event
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
                               units='deg',
                               color=txt_color)
    txt_stim.height = 1
    txt_stim.font = font

    # prepare image stim
    img_stim = visual.ImageStim(win)
    img_stim.pos = (0.5, 0)

    # general image directorys
    init_dir = op.dirname(sp_experiment.__file__)
    img_dir = op.join(init_dir, 'image_data')

    # START INSTRUCTIONS
    if kind == 'general':
        txt_stim.text = _provide_general_instr_str(lang=lang)
        txt_stim.draw()
        win.flip()
        event.waitKeys()

    elif kind == 'active':
        texts = _provide_active_instr_strs(lang=lang)
        for text in texts:
            txt_stim.text = text
            txt_stim.draw()
            if '' in text:
                img_stim.image = op.join(img_dir, 'bbtk_layout.png')
                img_stim.draw()

            win.flip()
            event.waitKeys()

    elif kind == 'passive':
        texts = _provide_passive_instr_strs(lang=lang)
        for text in texts:
            txt_stim.text = text
            txt_stim.draw()
            if '' in text:
                img_stim.image = './bbtk_layout.png'
                img_stim.draw()
            win.flip()
            event.waitKeys()

    win.close()


def _provide_active_instr_strs(lang='en'):
    """Provide active instr texts."""
    texts = list()
    if lang == 'de':
        pass
    elif lang == 'en':
        pass
    return texts


def _provide_passive_instr_strs(lang='en'):
    """Provide passive instr texts."""
    texts = list()
    if lang == 'de':
        pass
    elif lang == 'en':
        pass
    return texts


def _provide_general_instr_str(lang='en'):
    """Provide a welcome screen text."""
    if lang == 'de':
        welcome_str = ('Wilkommen! Sie werden zwei Aufgaben nacheinander '
                       'ausführen. Im Folgenden bekommen Sie Anweisungen zur '
                       'ersten Aufgabe. Dann dürfen Sie einen Test der '
                       'ersten Aufgabe durchführen. Danach wird die erste '
                       'Aufgabe gestartet. Wenn Sie mit dieser Aufgabe '
                       'fertig sind, wird die zweite Aufgabe in den selben '
                       'Schritten durchgeführt. Das heißt: Erst Anweisung, '
                       'dann Test, dann Durchführung der Aufgabe. '
                       'Druecken Sie eine beliebige Taste.')
    elif lang == 'en':
        welcome_str = ('Welcome! You will perform two tasks, one after the '
                       'other. In the following you will get instructions '
                       'for the first task. Then you are allowed to practice '
                       'the first task. Then you will perform the first task'
                       '. After you are done, the second task will be '
                       'started using the same procedure. That is, first '
                       'instructions, then practice, then execution of the '
                       'second task. Press any button.')
    return welcome_str


def provide_blockfbk_str(data_file, current_nblocks, nblocks, lang):
    """Provide a string to be displayed during block feedback.

    Parameters
    ----------
    data_file : str
        Path to the data file from which to calculate current amount of points.
    current_nblocks : int
    nblocks : int
    lang : str
        Language, can be 'de' or 'en' for German or English.

    Returns
    -------
    block_feedback : str

    """
    # Current number of points
    df_tmp = pd.read_csv(data_file, sep='\t')
    outcomes = get_final_choice_outcomes(df_tmp)
    points = int(np.sum(outcomes))

    if lang == 'de':
        block_feedback = (f'Block {current_nblocks}/{nblocks} beendet!'  # noqa: E999 E501
                          f' Sie haben bisher {points} Punkte gesammelt.'
                          ' Am Ende des Experiments werden Ihre Punkte'
                          ' in Euro umgerechnet und Ihnen als Bonus gezahlt.'
                          ' Machen Sie jetzt eine kurze Pause.'
                          ' Druecken Sie eine beliebige Taste um'
                          ' fortzufahren.')
    elif lang == 'en':
        block_feedback = (f'Block {current_nblocks}/{nblocks} done!'  # noqa: E999 E501
                          f' You earned {points} points so far.'
                          ' Remember that your points will be '
                          ' converted to Euros and paid to you at'
                          ' the end of the experiment as a bonus.'
                          ' Take a short break now.'
                          ' Then press any key to continue.')

    return block_feedback


def provide_start_str(is_test, condition, lang):
    """Provide a string for beginning of the task."""
    condi = 'A' if condition == 'active' else 'B'
    mod = ' TEST ' if is_test else ' '
    if lang == 'de':
        start_str = (f'Beginn der{mod}Aufgabe {condi}. Druecken Sie eine '
                     'beliebige Taste um zu beginnen.')
    elif lang == 'en':
        start_str = (f'Starting the{mod}for task {condi}. '
                     'Press any key to start.')
    return start_str


def provide_stop_str(is_test, lang):
    """Provide a string for end of the task."""
    mod = ' TEST ' if is_test else ' '
    if lang == 'de':
        stop_str = (f'Die{mod}Aufgabe ist beendet. Druecken Sie eine beliebige'
                    ' Taste.')
    elif lang == 'en':
        stop_str = f'The{mod}task is over. Press any key to quit.'

    return stop_str
