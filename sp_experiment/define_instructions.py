"""Functions that either provide an instruction flow or a string to display."""
import os
import os.path as op

import numpy as np
import pandas as pd
import tobii_research as tr

import sp_experiment
from sp_experiment.utils import get_final_choice_outcomes
from sp_experiment.define_settings import (txt_color, twait_show_instr,
                                           color_magnitude, color_probability,
                                           OPTIONAL_STOPPING)


def print_human_readable_instrs(kind, fpath=None):
    """Print the instructions in readable format.

    Parameters
    ----------
    kind : str
        Can be 'active', 'passive', or 'description'
    fpath : str | None
        Path to the file to be written. If None, will print to console. If
        file already exists, it will be deleted.

    """
    texts = run_instructions(kind, return_text_only=True)

    if fpath is None:
        for text in texts:
            print(text)
    else:
        if op.exists(fpath):
            os.remove(fpath)
        with open(fpath, 'w', encoding='utf-8') as fout:
            for text in texts:
                fout.write(text + '\n\n')


def run_instructions(kind, monitor='testMonitor', font='', lang='de',
                     max_ntrls=100, max_nsamples=12, block_size=25, maxwait=3,
                     exchange_rate=0.01, opt_stop=OPTIONAL_STOPPING,
                     return_text_only=False, track_eyes=False):
    """Show experiment instructions on the screen.

    Parameters
    ----------
    kind : str
        Can be 'general', 'active', 'passive', or 'description'
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
    opt_stop : bool
        True if optional stopping is allowed in this run, False otherwise ...
        see the experiment settings in define_settings.py
    return_text_only : bool
        If True, will only return the texts. No impact if False
    track_eyes : bool
        Defaults to False: will not change the instruction strings to
        accommodate for eyetracking. Will automatically switch to True if an
        eyetracker is detected in Runtime

    """
    if not return_text_only:
        from psychopy import visual, event, core

        # Check if we have an eyetracker
        found_eyetrackers = tr.find_all_eyetrackers()
        if len(found_eyetrackers) > 0:
            track_eyes = True

        # Define monitor specific window object
        win = visual.Window(color=(0, 0, 0),  # Background color: RGB [-1,1]
                            fullscr=True,  # Fullscreen for better timing
                            monitor=monitor,
                            winType='pyglet')

        # Hide the cursor
        win.mouseVisible = False

        # prepare text object
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
        texts = _provide_general_instr_str(lang=lang)
        if return_text_only:
            return texts
        for text in texts:
            txt_stim.text = text
            txt_stim.draw()
            win.flip()
            core.wait(twait_show_instr)  # force some wait time
            key = event.waitKeys()
            if key[0] == 'x':
                break

    elif kind == 'active':
        texts = _provide_active_instr_strs(lang, max_ntrls, max_nsamples,
                                           block_size, maxwait, exchange_rate,
                                           track_eyes, opt_stop)
        if return_text_only:
            return texts
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
            if 'zentralen Stimulus weiß' in text:
                img_stim.image = op.join(img_dir, 'action_cropped.png')
                img_stim.draw()
            if 'kurz zu blau' in text:
                img_stim.image = op.join(img_dir, 'choice_cropped.png')
                img_stim.draw()
            if 'Sekunden Zeit' in text:
                img_stim.image = op.join(img_dir, 'error_cropped.png')
                img_stim.draw()
            if 'Zusammenfassend' in text:
                img_stim.image = op.join(img_dir, 'fix_stims.png')
                img_stim.draw()
            win.flip()
            core.wait(twait_show_instr)  # force some wait time
            key = event.waitKeys()
            if key[0] == 'x':
                break

    elif kind == 'passive':
        texts = _provide_passive_instr_strs(lang, max_ntrls, max_nsamples,
                                            block_size, maxwait, exchange_rate,
                                            track_eyes, opt_stop)
        if return_text_only:
            return texts
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
            if 'zentralen Stimulus weiß' in text:
                img_stim.image = op.join(img_dir, 'action_cropped.png')
                img_stim.draw()
            if 'kurz zu blau' in text:
                img_stim.image = op.join(img_dir, 'choice_cropped.png')
                img_stim.draw()
            if 'Sekunden Zeit' in text:
                img_stim.image = op.join(img_dir, 'error_cropped.png')
                img_stim.draw()
            if 'Zusammenfassend' in text:
                img_stim.image = op.join(img_dir, 'fix_stims.png')
                img_stim.draw()
            win.flip()
            core.wait(twait_show_instr)  # force some wait time
            key = event.waitKeys()
            if key[0] == 'x':
                break

    elif kind == 'description':
        texts = _provide_description_instr_str(lang=lang)
        if return_text_only:
            return texts
        for text in texts:
            txt_stim.text = text
            txt_stim.draw()

            # Draw red and blue lottery
            txt_stim1 = visual.TextStim(win, units='deg',
                                        color=color_magnitude,
                                        height=1, font=font, text='1\n5',
                                        pos=(-0.5, -7))
            txt_stim2 = visual.TextStim(win, units='deg',
                                        color=color_probability,
                                        height=1, font=font, text='90\n10',
                                        pos=(0.5, -7))

            txt_stim1.draw()
            txt_stim2.draw()
            # Flip and go
            win.flip()
            core.wait(twait_show_instr)  # force some wait time
            key = event.waitKeys()
            if key[0] == 'x':
                break

    win.close()


def _provide_active_instr_strs(lang, max_ntrls, max_nsamples, block_size,
                               maxwait, exchange_rate, track_eyes,
                               opt_stop=OPTIONAL_STOPPING):
    """Provide active instr texts."""
    # Eyetracking special replacement strings
    if track_eyes:
        eyetrackstr1 = ' Wenn Sie während eines Versuchs wiederholt nicht ausreichend fixieren, muss der Versuch erneut gestartet werden.'  # noqa: E501
        eyetrackstr2 = ' Die Farbe wechselt auch zu rot, wenn Sie wiederholt nicht ausreichend den zentralen Stimulus fixiert haben.'  # noqa: E501
        eyetrackstr3 = 'oder haben wiederholt nicht den zentralen Stimulus fixiert '  # noqa: E501
    else:
        eyetrackstr1 = ''
        eyetrackstr2 = ''
        eyetrackstr3 = ''

    # Optional stopping special replacement strings
    if opt_stop:
        opt_stop_str1 = 'bis zu einem Maximum von {}'.format(max_nsamples)
        opt_stop_str2 = 'von Ihnen gewählte Anzahl an Kugeln (bis zu maximal {})'.format(max_nsamples)  # noqa: E501
        opt_stop_str3 = 'nach dem Drücken der "Stopp" Taste oder '
        opt_stop_str4 = 'maximal {}'.format(max_nsamples)
    else:
        opt_stop_str1 = max_nsamples
        opt_stop_str2 = '{} Kugeln'.format(max_nsamples)
        opt_stop_str3 = ''
        opt_stop_str4 = '{}'.format(max_nsamples)

    texts = list()
    if lang == 'de':
        texts.append('Instruktionen Aufgabe A. Bitte lesen Sie aufmerksam den folgenden Text. Drücken Sie eine beliebige Taste um fortzufahren. Achten Sie auf die Details in der Beschreibung! In dieser Aufgabe werden Sie selbst nach Informationen suchen.')  # noqa: E501
        texts.append('Bitte fixieren Sie während des Experiments mit ihrem Blick immer den zentralen Stimulus in der Bildschirmmitte.{}'.format(eyetrackstr1))  # noqa: E501
        texts.append('Links und rechts von dem zentralen Stimulus befinden sich zwei unsichtbare Urnen. In den Urnen befinden sich jeweils zehn Kugeln mit Zahlen darauf. Die Zahlen stehen für Spielpunkte, die zu einem Wechselkurs von {} in Euro umgewandelt werden. Dieses Geld in Euro wird Ihnen am Ende des Experimentes als Bonus ausgezahlt.'.format(exchange_rate))  # noqa: E501
        texts.append('Es gibt in dieser Aufgabe viele Durchgänge. In jedem Durchgang gibt es neue Urnen, und ihre Aufgabe wird jedes Mal sein, sich am Ende der Aufgabe für eine der beiden Urnen zu entscheiden. Um etwas über den Inhalt der Urnen zu erfahren, dürfen Sie in jedem Durchgang zunächst insgesamt {} mal blind eine Kugel ziehen. Dies können Sie tun, indem Sie die linke oder die rechte Taste drücken. Sie können also jedes Mal selbst wählen, aus welcher Urne die nächste Kugel gezogen wird. Die Kugel wird jedesmal  zufällig aus der jeweiligen Urne gezogen und Ihnen kurz gezeigt. Danach wird die Kugel zurück in die ursprüngliche Urne gelegt. Es sind also IMMER 10 Kugeln in jeder Urne. In anderen Worten, der Inhalt der Urnen wird durch Ihre Ziehung(en) nicht verändert.'.format(opt_stop_str1))  # noqa: E501 E999
        if opt_stop:
            # If optional stopping, append an extra explanation on how to stop
            texts.append('Wie bereits erwähnt können Sie in jedem Durchgang maximal {} mal blind eine Kugel ziehen, um mehr über die Urnen zu lernen. Sie können jedoch auch schon früher aufhören, Kugeln zu ziehen. Das können Sie mit der Taste über der rechten Tase anzeigen. Beim Drücken der dieser "Stopp" Taste wird sofort die nächste Phase des momentanen Durchgangs eingeleitet, wie im Folgenden beschrieben.')  # noqa: E501
        texts.append('Nachdem Sie sich die {} angeschaut haben, müssen Sie sich final für eine der Urnen entscheiden. Ihr Ziel sollte natürlich sein, dabei immer die jeweils bessere Urne zu wählen. Nach dieser finalen Entscheidung wird aus der gewählten Urne nochmals eine Kugel (zufällig) gezogen. Die Punkte auf dieser finalen Kugel werden Ihrem Konto gutgeschrieben. Dies wird durch die grüne Farbe der Punkte gezeigt. Danach beginnt ein neuer Durchgang mit komplett neuen Urnen. Insgesamt gibt es {} Durchgänge und alle {} Durchgänge werden Sie Zeit für eine kurze Pause haben.'.format(opt_stop_str2, max_ntrls, block_size))  # noqa: E501
        texts.append('Als Hilfestellung zeigt Ihnen die Farbe des zentralen Stimulus an, was während der Durchgänge als nächstes passiert: Zu Beginn eines Durchgangs ist der Stimulus kurz grün und dann weiß. Das bedeutet, dass neue unsichtbaren Urnen links und rechts aufgestellt wurden.')  # noqa: E501
        texts.append('Danach bleibt die Farbe des zentralen Stimulus weiß. Das bedeutet, dass Sie jetzt eine Kugel aus einer der Urnen ziehen können, durch Drücken der linken oder der rechten Taste. Während Sie darauf warten, dass die Kugel gezeigt wird, wird die Farbe des zentralen Stimulus auch noch weiß sein.')  # noqa: E501
        texts.append('Wenn Sie {}nach {} Zügen ein weiteres Mal die linke oder rechte Taste drücken, wechselt die Farbe des zentralen Stimulus kurz zu blau und wird dann wieder weiß. Das bedeutet, dass Sie sich nun final zwischen den Urnen entscheiden müssen. Zur Erinnerung: Nur die Kugel die nach der finalen Entscheidung gezogen wird bestimmt, wie viele Punkte ihrem Konto hinzugefügt werden.'.format(opt_stop_str3, opt_stop_str4))  # noqa: E501
        texts.append('Für Ihre Entscheidungen haben Sie jeweils {} Sekunden Zeit. Wenn Sie länger warten, wechselt die Farbe des zentralen Stimulus zu rot und der momentane Durchgang wird abgebrochen.{} Direkt danach wird ein neuer Durchgang gestartet.'.format(maxwait, eyetrackstr2))  # noqa: E501
        texts.append('Zusammenfassend bedeuten die Farben das folgende:\n\ngrün: neuer Durchgang mit neuen Urnen\n\nweiß: Urne wählen oder auf zufällig gezogene Kugel warten\n\nblau: nächste Entscheidung ist die finale Entscheidung für diesen Durchgang\n\nrot: Sie haben länger als {} Sekunden gewartet {}und der Durchgang wird abgebrochen'.format(maxwait, eyetrackstr3))  # noqa: E501
        texts.append('Die Instruktionen sind abgeschlossen. Drücken Sie eine beliebige Taste um fortzufahren.')  # noqa: E501

    elif lang == 'en':
        texts.append('LANGUAGE NOT IMPLEMENTED YET')
    return texts


def _provide_passive_instr_strs(lang, max_ntrls, max_nsamples, block_size,
                                maxwait, exchange_rate, track_eyes,
                                opt_stop=OPTIONAL_STOPPING):
    """Provide passive instr texts."""
    # Eyetracking special replacement strings
    if track_eyes:
        eyetrackstr1 = ' Wenn Sie während eines Versuchs wiederholt nicht ausreichend fixieren, muss der Versuch erneut gestartet werden.'  # noqa: E501
        eyetrackstr2 = ' Die Farbe wechselt auch zu rot, wenn Sie wiederholt nicht ausreichend den zentralen Stimulus fixiert haben.'  # noqa: E501
        eyetrackstr3 = 'oder haben wiederholt nicht den zentralen Stimulus fixiert '  # noqa: E501
    else:
        eyetrackstr1 = ''
        eyetrackstr2 = ''
        eyetrackstr3 = ''

    # Optional stopping special replacement strings
    if opt_stop:
        opt_stop_str1 = 'bis zu einem Maximum von {}'.format(max_nsamples)
        opt_stop_str2 = 'vom Computer gewählte Anzahl an Kugeln (bis zu maximal {})'.format(max_nsamples)  # noqa: E501
        opt_stop_str3 = 'nach dem Drücken der "Stopp" Taste oder '
        opt_stop_str4 = 'maximal {}'.format(max_nsamples)
    else:
        opt_stop_str1 = max_nsamples
        opt_stop_str2 = '{} Kugeln'.format(max_nsamples)
        opt_stop_str3 = ''
        opt_stop_str4 = '{}'.format(max_nsamples)

    texts = list()
    if lang == 'de':
        texts.append('Instruktionen Aufgabe B. Bitte lesen Sie aufmerksam den folgenden Text. Drücken Sie eine beliebige Taste um fortzufahren. Achten Sie auf die Details in der Beschreibung! In dieser Aufgabe wird der Computer Sie mit Informationen versorgen.')  # noqa: E501
        texts.append('Bitte fixieren Sie während des Experiments mit ihrem Blick immer den zentralen Stimulus in der Bildschirmmitte.{}'.format(eyetrackstr1))  # noqa: E501
        texts.append('Links und rechts von dem zentralen Stimulus befinden sich zwei unsichtbare Urnen. In den Urnen befinden sich jeweils zehn Kugeln mit Zahlen darauf. Die Zahlen stehen für Spielpunkte, die zu einem Wechselkurs von {} in Euro umgewandelt werden. Dieses Geld in Euro wird Ihnen am Ende des Experimentes als Bonus ausgezahlt.'.format(exchange_rate))  # noqa: E501
        texts.append('Es gibt in dieser Aufgabe viele Durchgänge. In jedem Durchgang gibt es neue Urnen, und ihre Aufgabe wird jedes Mal sein, sich am Ende der Aufgabe für eine der beiden Urnen zu entscheiden. Der Computer wird zunächst insgesamt {} mal blind eine Kugel ziehen. Hierzu wird der Computer entscheiden,  aus welcher Urne die nächste Kugel gezogen wird. Die Kugel wird jedesmal  zufällig aus der jeweiligen Urne gezogen und Ihnen kurz gezeigt. Danach wird die Kugel zurück in die ursprüngliche Urne gelegt. Es sind also IMMER 10 Kugeln in jeder Urne. In anderen Worten, der Inhalt der Urnen wird durch Ihre Ziehung(en) nicht verändert.'.format(opt_stop_str1))  # noqa: E501
        texts.append('Nachdem Sie sich die {} angeschaut haben, müssen Sie sich final für eine der Urnen entscheiden. Dies können Sie tun, indem Sie die linke oder die rechte Taste drücken. Ihr Ziel sollte natürlich sein, dabei immer die jeweils bessere Urne zu wählen. Nach dieser finalen Entscheidung wird aus der gewählten Urne nochmals eine Kugel (zufällig) gezogen. Die Punkte auf dieser finalen Kugel werden Ihrem Konto gutgeschrieben.'.format(opt_stop_str2))  # noqa: E501
        texts.append('Dies wird durch die grüne Farbe der Punkte gezeigt. Danach beginnt ein neuer Durchgang mit komplett neuen Urnen. Insgesamt gibt es {} Durchgänge und alle {} Durchgänge werden Sie Zeit für eine kurze Pause haben.'.format(max_ntrls, block_size))  # noqa: E501
        texts.append('Als Hilfestellung zeigt Ihnen die Farbe des zentralen Stimulus an, was während der Durchgänge als nächstes passiert: Zu Beginn eines Durchgangs ist der Stimulus kurz grün und dann weiß. Das bedeutet, dass neue unsichtbaren Urnen links und rechts aufgestellt wurden.')  # noqa: E501
        texts.append('Danach bleibt die Farbe des zentralen Stimulus weiß. Das bedeutet, dass der Computer jetzt eine Kugel aus einer der Urnen ziehen wird. Während Sie darauf warten, dass die Kugel gezeigt wird, wird die Farbe des zentralen Stimulus auch noch weiß sein.')  # noqa: E501
        texts.append('Wenn der Computer {} Züge getätigt hat, wechselt die Farbe des zentralen Stimulus kurz zu blau und wird dann wieder weiß. Das bedeutet, dass Sie sich nun final zwischen den Urnen entscheiden müssen. Zur Erinnerung: Nur die Kugel die nach der finalen Entscheidung gezogen wird bestimmt, wie viele Punkte ihrem Konto hinzugefügt werden.'.format(max_nsamples))  # noqa: E501
        texts.append('Für Ihre Entscheidungen haben Sie jeweils {} Sekunden Zeit. Wenn Sie länger warten, wechselt die Farbe des zentralen Stimulus zu rot und der momentane Durchgang wird abgebrochen.{} Direkt danach wird ein neuer Durchgang gestartet.'.format(maxwait, eyetrackstr2))  # noqa: E501
        texts.append('Zusammenfassend bedeuten die Farben das folgende:\n\ngrün: neuer Durchgang mit neuen Urnen\n\nweiß: Der Computer wählt eine Urne oder auf zufällig gezogene Kugel warten\n\nblau: nächste Entscheidung ist die finale Entscheidung für diesen Durchgang\n\nrot: Sie haben länger als {} Sekunden gewartet {}und der Durchgang wird abgebrochen'.format(maxwait, eyetrackstr3))  # noqa: E501
        texts.append('Die Instruktionen sind abgeschlossen. Drücken Sie eine beliebige Taste um fortzufahren.')  # noqa: E501

    elif lang == 'en':
        texts.append('LANGUAGE NOT IMPLEMENTED YET')
    return texts


def _provide_general_instr_str(lang):
    """Provide a welcome screen text."""
    texts = list()
    if lang == 'de':
        welcome_str = ('Wilkommen! Sie werden drei Aufgaben nacheinander '
                       'ausführen. Im Folgenden bekommen Sie Anweisungen zur '
                       'ersten Aufgabe. Dann dürfen Sie einen Test der '
                       'ersten Aufgabe durchführen. Danach wird die erste '
                       'Aufgabe gestartet. Wenn Sie mit dieser Aufgabe '
                       'fertig sind, wird die zweite Aufgabe in den selben '
                       'Schritten durchgeführt. Das heißt: Erst Anweisung, '
                       'dann Test, dann Durchführung der Aufgabe. '
                       'Zum Schluss gibt es noch eine kurze dritte Aufgabe. '
                       'Drücken Sie eine beliebige Taste.')
    elif lang == 'en':
        welcome_str = ('Welcome! You will perform three tasks, one after the '
                       'other. In the following you will get instructions '
                       'for the first task. Then you are allowed to practice '
                       'the first task. Then you will perform the first task'
                       '. After you are done, the second task will be '
                       'started using the same procedure. That is, first '
                       'instructions, then practice, then execution of the '
                       'second task. Finally, there will be a short third '
                       'task. Press any button.')
    texts.append(welcome_str)
    return texts


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
        block_feedback = ('Block {}/{} beendet!'  # noqa: E999 E501
                          ' Sie haben in dieser Aufgabe bisher {} '
                          'Punkte gesammelt.'
                          ' Am Ende des Experiments werden Ihre Punkte'
                          ' in Euro umgerechnet und Ihnen als Bonus gezahlt.'
                          ' Machen Sie jetzt eine kurze Pause.'
                          ' Drücken Sie eine beliebige Taste um'
                          ' fortzufahren.'
                          .format(current_nblocks, nblocks, points))
    elif lang == 'en':
        block_feedback = ('Block {}/{} done!'  # noqa: E999 E501
                          ' You earned {} points in this task '
                          'so far.'
                          ' Remember that your points will be '
                          ' converted to Euros and paid to you at'
                          ' the end of the experiment as a bonus.'
                          ' Take a short break now.'
                          ' Then press any key to continue.'
                          .format(current_nblocks, nblocks, points))

    return block_feedback


def provide_start_str(is_test, condition, lang):
    """Provide a string for beginning of the task."""
    if condition == 'active':
        condi = 'A'
    elif condition == 'passive':
        condi = 'B'
    else:
        condi = 'C'
    mod = ' TEST ' if is_test else ' '
    if lang == 'de':
        start_str = ('Beginn der{}Aufgabe {}. Drücken Sie eine '
                     'beliebige Taste um zu beginnen.'
                     .format(mod, condi))
    elif lang == 'en':
        start_str = ('Starting the{}for task {}. '
                     'Press any key to start.'
                     .format(mod, condi))
    return start_str


def provide_stop_str(is_test, lang):
    """Provide a string for end of the task."""
    mod = ' TEST ' if is_test else ' '
    if lang == 'de':
        stop_str = ('Die{}Aufgabe ist beendet. Drücken Sie eine beliebige'
                    ' Taste.'.format(mod))
    elif lang == 'en':
        stop_str = 'The{}task is over. Press any key to quit.'.format(mod)

    return stop_str


def _provide_description_instr_str(lang='de'):
    """Provide instructions."""
    texts = list()
    if lang == 'de':
        instruct_str = ('Im Folgenden werden Sie auf der linken und rechten '
                        'Seite jeweils eine Lotterie sehen. Benutzen Sie die '
                        'linke oder rechte Taste, um sich für die Lotterie '
                        'zu entscheiden, die Sie spielen wollen. '
                        'Danach wird ihnen ihr Gewinn angezeigt.')
        instruct_str += ('Unten sehen Sie ein Beispiel für *eine* Lotterie. '
                         'Diese Lotterie bedeutet: 1 Punkt mit 90%iger oder '
                         '5 Punkte mit 10%iger Chance. Die Punktzahl wird '
                         'in pink angezeigt, die Wahrscheinlichkeit in blau.')
        instruct_str += ('\n\n\n\n\nDrücken Sie eine beliebige Taste um zu '
                         'beginnen.')

        texts.append(instruct_str)

    elif lang == 'en':
        raise RuntimeError('English language not yet implemented.')

    return texts
