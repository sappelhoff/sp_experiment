"""Functions that either provide an instruction flow or a string to display."""
import os.path as op

import numpy as np
import pandas as pd

import sp_experiment
from sp_experiment.utils import get_final_choice_outcomes


def run_instructions(kind, monitor='testMonitor', font='', lang='en',
                     max_ntrls=100, max_nsamples=12, block_size=25, maxwait=3,
                     exchange_rate=0.1):
    """Show experiment instructions on the screen.

    Parameters
    ----------
    kind : str
        Can be 'general', 'active', and 'passive'.
    monitor : str
        Name of monitor to be used
    font : str
        Name of font to be used
    lang : str
        Language to be used, can be 'de' or 'en'
    max_ntrls : int
        Maximum number of trials for this run.
    max_nsamples : int
        Maximum number of samples per trial.
    block_size : int
        Number of trials after which feedback is provided
    maxwait : int | float
        Maximum time to wait for a response until time out
    exchange_rate : float
        Conversion rate of points to Euros

    """
    from psychopy import visual, event, core
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
        core.wait(2)  # force some wait time
        key = event.waitKeys()
        if key[0] == 'x':
            core.quit()

    elif kind == 'active':
        texts = _provide_active_instr_strs(lang, max_ntrls, max_nsamples,
                                           block_size, maxwait, exchange_rate)
        for text in texts:
            txt_stim.text = text
            txt_stim.draw()
            if 'Kugeln mit Zahlen' in text:
                img_stim.image = op.join(img_dir, 'any_ball.png')
                img_stim.draw()
            if 'Taste drücken.' in text:
                img_stim.image = op.join(img_dir, 'bbox_photo.png')
                img_stim.draw()
            if 'Farbe der Punkte' in text:
                img_stim.image = op.join(img_dir, 'final_ball.png')
                img_stim.draw()
            if 'Hilfestellung' in text:
                img_stim.image = op.join(img_dir, 'start_cropped.png')
                img_stim.draw()
            if '(Die Farbe' in text:
                img_stim.image = op.join(img_dir, 'action_cropped.png')
                img_stim.draw()
            if 'Zügen' in text:
                img_stim.image = op.join(img_dir, 'choice_cropped.png')
                img_stim.draw()
            if 'länger brauchen' in text:
                img_stim.image = op.join(img_dir, 'error_cropped.png')
                img_stim.draw()
            if 'Zusammenfassend' in text:
                img_stim.image = op.join(img_dir, 'fix_stims.png')
                img_stim.draw()
            win.flip()
            core.wait(2)  # force some wait time
            key = event.waitKeys()
            if key[0] == 'x':
                core.quit()

    elif kind == 'passive':
        texts = _provide_passive_instr_strs(lang, max_ntrls, max_nsamples,
                                            block_size, maxwait, exchange_rate)
        for text in texts:
            txt_stim.text = text
            txt_stim.draw()
            if 'Kugeln mit Zahlen' in text:
                img_stim.image = op.join(img_dir, 'any_ball.png')
                img_stim.draw()
            if 'Taste drücken.' in text:
                img_stim.image = op.join(img_dir, 'bbox_photo.png')
                img_stim.draw()
            if 'Farbe der Punkte' in text:
                img_stim.image = op.join(img_dir, 'final_ball.png')
                img_stim.draw()
            if 'Hilfestellung' in text:
                img_stim.image = op.join(img_dir, 'start_cropped.png')
                img_stim.draw()
            if '(Die Farbe' in text:
                img_stim.image = op.join(img_dir, 'action_cropped.png')
                img_stim.draw()
            if 'Zügen' in text:
                img_stim.image = op.join(img_dir, 'choice_cropped.png')
                img_stim.draw()
            if 'länger brauchen' in text:
                img_stim.image = op.join(img_dir, 'error_cropped.png')
                img_stim.draw()
            if 'Zusammenfassend' in text:
                img_stim.image = op.join(img_dir, 'fix_stims.png')
                img_stim.draw()
            win.flip()
            core.wait(2)  # force some wait time
            key = event.waitKeys()
            if key[0] == 'x':
                core.quit()
    win.close()


def _provide_active_instr_strs(lang, max_ntrls, max_nsamples, block_size,
                               maxwait, exchange_rate):
    """Provide active instr texts."""
    texts = list()
    if lang == 'de':
        texts.append('Instruktionen Aufgabe *A*. Bitte lesen Sie aufmerksam den folgenden Text. Drücken Sie eine beliebige Taste um fortzufahren.')  # noqa: E501
        texts.append(f'Bitte fixieren Sie während des Experiments mit ihrem Blick immer den zentralen Stimulus in der Bildschirmmitte. Links und rechts von diesem Stimulus befinden sich zwei unsichtbare Urnen. In den Urnen befinden sich mehrere Kugeln mit Zahlen darauf. Die Zahlen stehen für Spielpunkte, die zu einen Wechselkurs von {exchange_rate} in Euro umgewandelt werden. Dieses Geld in Euro wird Ihnen am Ende des Experimentes als Bonus ausgezahlt.')  # noqa: E501 E999
        texts.append(f'Es gibt in dieser Aufgabe viele Durchgänge. In jedem Durchgang gibt es neue Urnen, und ihre Aufgabe wird jedes Mal sein, sich am Ende der Aufgabe für eine der beiden Urnen zu entscheiden. Um etwas über den Inhalt der Urnen zu erfahren, dürfen Sie in jedem Durchgang  insgesamt {max_nsamples} Kugeln ziehen. Dies können Sie tun, indem Sie die linke oder die rechte Taste drücken. Sie können also jedes Mal selbst wählen, aus welcher Urne die nächste Kugel gezogen wird. Die gezogene Kugel wir Ihnen kurz gezeigt, und danach zurück in die Urne gelegt.')  # noqa: E501 E999
        texts.append(f'Nachdem Sie sich die {max_nsamples} Kugeln angeschaut haben, müssen Sie sich final für einer der Urnen entscheiden. Ihr Ziel sollte natürlich  sein, dabei immer die jeweils bessere Urne zu wählen. Nach dieser finalen Entscheidung wird aus der gewählten Urne nochmals eine Kugel gezogen. Die Punkte auf dieser finalen Kugel werden Ihrem Konto gutgeschrieben. Dies wird durch die grüne Farbe der Punkte gezeigt. Danach beginnt ein neuer Durchgang mit neuen Urnen. Insgesamt gibt es {max_ntrls} Durchgänge und alle {block_size} Durchgänge werden Sie Zeit für eine kurze Pause haben.')  # noqa: E501
        texts.append('Als Hilfestellung zeigt Ihnen die Farbe des zentralen Stimulus an, was während der Durchgänge als nächstes passiert: Zu Beginn eines Durchgangs ist der Stimulus kurz grün und dann weiß. Das bedeutet, dass neue unsichtbaren Urnen links und rechts aufgestellt wurden.')  # noqa: E501
        texts.append('Dann bleibt die Farbe des zentralen Stimulus weiß. Das bedeutet, dass Sie jetzt eine Kugel aus eine der Urnen ziehen können mit der linken oder der rechten Taste. (Die Farbe des zentralen Stimulus ist auch weiß, wenn Sie darauf warten, dass die Kugel gezeigt wird.)')  # noqa: E501
        texts.append(f'Wenn Sie nach {max_nsamples} Zügen ein weiteres Mal die linke oder rechte Taste drücken, wechselt die Farbe des zentralen Stimulus kurz zu blau und wird dann wieder weiß. Das bedeutet, dass Sie sich nun final zwischen den Urnen entscheiden müssen. Zur Erinnerung: Nur die Kugel die nach der finalen Entscheidung gezogen wird bestimmt, wie viele Punkte ihrem Konto hinzugefügt werden.')  # noqa: E501
        texts.append(f'Für Ihre Entscheidungen haben Sie jeweils {maxwait} Sekunden Zeit. Wenn Sie länger brauchen, wechselt die Farbe des zentralen Stimulus zu rot und der momentane Durchgang wird abgebrochen. Direkt danach wird ein neuer Durchgang gestartet.')  # noqa: E501
        texts.append(f'Zusammenfassend bedeuten die Farben das folgende:\n\ngrün: neuer Durchgang mit neuen Urnen\n\nweiß: Urne wählen oder auf Kugel warten\n\nblau: nächste Entscheidung ist eine finale Entscheidung für den Durchgang\n\nrot: Sie haben länger als {maxwait} Sekunden gewartet und der Durchgang wird abgebrochen')  # noqa: E501
        texts.append('Die Instruktionen sind abgeschlossen. Drücken Sie eine beliebige Taste um fortzufahren.')  # noqa: E501

    elif lang == 'en':
        texts.append('LANGUAGE NOT IMPLEMENTED YET')
    return texts


def _provide_passive_instr_strs(lang, max_ntrls, max_nsamples, block_size,
                                maxwait, exchange_rate):
    """Provide passive instr texts."""
    texts = list()
    if lang == 'de':
        texts.append('Instruktionen Aufgabe *B*. Bitte lesen Sie aufmerksam den folgenden Text. Drücken Sie eine beliebige Taste um fortzufahren.')  # noqa: E501
        texts.append(f'Bitte fixieren Sie während des Experiments mit ihrem Blick immer den zentralen Stimulus in der Bildschirmmitte. Links und rechts von diesem Stimulus befinden sich zwei unsichtbare Urnen. In den Urnen befinden sich mehrere Kugeln mit Zahlen darauf. Die Zahlen stehen für Spielpunkte, die zu einen Wechselkurs von {exchange_rate} in Euro umgewandelt werden. Dieses Geld in Euro wird Ihnen am Ende des Experimentes als Bonus ausgezahlt.')  # noqa: E501
        texts.append(f'Es gibt in dieser Aufgabe viele Durchgänge. In jedem Durchgang gibt es neue Urnen, und ihre Aufgabe wird jedes Mal sein, sich am Ende der Aufgabe für eine der beiden Urnen zu entscheiden. Der Computer wird in jedem Durchgang insgesamt {max_nsamples} Kugeln ziehen. So können Sie etwas über den Inhalt der Urnen zu erfahren, denn die gezogene Kugel wir Ihnen kurz gezeigt, und danach zurück in die Urne gelegt.')  # noqa: E501
        texts.append(f'Nachdem Sie sich die {max_nsamples} Kugeln angeschaut haben, müssen Sie sich final für eine der Urnen entscheiden. Dies können Sie tun, indem Sie die linke oder die rechte Taste drücken. Ihr Ziel sollte natürlich  sein, dabei immer die jeweils bessere Urne zu wählen.')  # noqa: E501
        texts.append(f'Nach Ihrer aktiven Entscheidung wird aus der gewählten Urne eine Kugel gezogen. Die Punkte auf dieser finalen Kugel werden Ihrem Konto gutgeschrieben. Dies wird durch die grüne Farbe der Punkte gezeigt. Danach beginnt ein neuer Durchgang mit neuen Urnen. Insgesamt gibt es {max_ntrls} Durchgänge und alle {block_size} Durchgänge werden Sie Zeit für eine kurze Pause haben.')  # noqa: E501
        texts.append('Als Hilfestellung zeigt Ihnen die Farbe des zentralen Stimulus an, was während der Durchgänge als nächstes passiert: Zu Beginn eines Durchgangs ist der Stimulus kurz grün und dann weiß. Das bedeutet, dass neue unsichtbaren Urnen links und rechts aufgestellt wurden.')  # noqa: E501
        texts.append('Dann bleibt die Farbe des zentralen Stimulus weiß. Das bedeutet, dass der Computer jetzt eine Kugel aus einer der Urnen ziehen wird. (Die Farbe des zentralen Stimulus ist auch weiß, wenn Sie darauf warten, dass die Kugel gezeigt wird.)')  # noqa: E501
        texts.append(f'Wenn der Computer {max_nsamples} Zügen getätigt hat, wechselt die Farbe des zentralen Stimulus kurz zu blau und wird dann wieder weiß. Das bedeutet, dass Sie sich nun aktiv zwischen den Urnen entscheiden müssen. Zur Erinnerung: Nur die Kugel die nach der finalen Entscheidung gezogen wird bestimmt, wie viele Punkte ihrem Konto hinzugefügt werden.')  # noqa: E501
        texts.append(f'Für Ihre Entscheidungen haben Sie jeweils {maxwait} Sekunden Zeit. Wenn Sie länger brauchen, wechselt die Farbe des zentralen Stimulus zu rot und der momentane Durchgang wird abgebrochen. Direkt danach wird ein neuer Durchgang gestartet.')  # noqa: E501
        texts.append(f'Zusammenfassend bedeuten die Farben das folgende:\n\ngrün: neuer Durchgang mit neuen Urnen\n\nweiß: Computer wählt eine Urne oder auf Kugel warten\n\nblau: nächste Entscheidung ist eine aktive Entscheidung für den Durchgang\n\nrot: Sie haben länger als {maxwait} Sekunden gewartet und der Durchgang wird abgebrochen')  # noqa: E501
        texts.append('Die Instruktionen sind abgeschlossen. Drücken Sie eine beliebige Taste um fortzufahren.')  # noqa: E501

    elif lang == 'en':
        texts.append('LANGUAGE NOT IMPLEMENTED YET')
    return texts


def _provide_general_instr_str(lang):
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
                       'Drücken Sie eine beliebige Taste.')
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
                          ' Drücken Sie eine beliebige Taste um'
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
        start_str = (f'Beginn der{mod}Aufgabe {condi}. Drücken Sie eine '
                     'beliebige Taste um zu beginnen.')
    elif lang == 'en':
        start_str = (f'Starting the{mod}for task {condi}. '
                     'Press any key to start.')
    return start_str


def provide_stop_str(is_test, lang):
    """Provide a string for end of the task."""
    mod = ' TEST ' if is_test else ' '
    if lang == 'de':
        stop_str = (f'Die{mod}Aufgabe ist beendet. Drücken Sie eine beliebige'
                    ' Taste.')
    elif lang == 'en':
        stop_str = f'The{mod}task is over. Press any key to quit.'

    return stop_str


def instruct_str_descriptions(lang='en'):
    """Provide instructions."""
    if lang == 'de':
        instruct_str = ('Im Folgenden werden Sie auf der linken und rechten '
                        'Seite jeweils eine Lotterie sehen. Benutzen Sie die '
                        'linke oder rechte Taste, um sich fuer die Lotterie '
                        'entscheiden, die Sie fuer profitabler halten.'
                        '\n\nBeispiel:\n\n')
        instruct_str += '1 - 90%    |    2 - 80%\n3 - 10%    |    4 - 20%'
        instruct_str += '\n\n'
        instruct_str += ('Linke lotterie: 1 Punkt mit 90%iger oder '
                         '5 Punkte mit 10%iger Chance')
        instruct_str += '\n\ngegen\n\n'
        instruct_str += ('Rechte Lotterie: 2 Punkte mit 80%iger oder '
                         '3 Punkte with 20%iger Chance')
        instruct_str += '\n\nDrücken Sie eine beliebige Taste um zu beginnen.'

    elif lang == 'en':
        instruct_str = ('In the following you will be presented with '
                        'lotteries on the left and right side of the screen. '
                        'Use the left and right key to select the lottery '
                        'that you deem more profitable.'
                        '\n\nExample:\n\n')
        instruct_str += '1 - 90%    |    2 - 80%\n3 - 10%    |    4 - 20%'
        instruct_str += '\n\n'
        instruct_str += ('Lottery left: 1 point with 90% or '
                         '3 points with 10% chance')
        instruct_str += '\n\nversus\n\n'
        instruct_str += ('Lottery right: 2 points with 80% '
                         'or a 4 points with 20% chance')
        instruct_str += '\n\nPress any key to begin.'
    return instruct_str
