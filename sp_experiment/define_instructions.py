"""Functions that either provide an instruction flow or a string to display."""
import numpy as np
import pandas as pd

from sp_experiment.utils import get_final_choice_outcomes


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
                           ' Druecken Sie einen beliebigen Knopf um'
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
