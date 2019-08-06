"""Test the experiment generator function."""
from collections import OrderedDict

import pytest
import numpy as np
import pandas as pd

from sp_experiment.define_settings import provide_experimental_design


def test_provide_experimental_design():
    """Test providing an experimental design."""
    n_participants = 4
    yokes, opt_stops, seeds = provide_experimental_design(n_participants)

    for dd in yokes, opt_stops, seeds:
        assert isinstance(dd, OrderedDict)
        assert list(dd.keys()) == [1, 2, 3, 4]

    assert list(yokes.values()) == [1, 2, 1, 2]
    assert list(opt_stops.values()) == [False, True, False, True]
    assert list(seeds.values()) == [1, 1, 1, 1]

    with pytest.raises(ValueError, match='4'):
        provide_experimental_design(5)

    # print the actual design
    n_participants = 40
    yokes, opt_stops, seeds = provide_experimental_design(n_participants)
    df = pd.DataFrame(np.arange(1, n_participants+1), columns=['sub_id'])
    df['yoked_to'] = df['sub_id'].map(yokes)
    df['opt_stop'] = df['sub_id'].map(opt_stops)
    df['seed'] = df['sub_id'].map(seeds)
    df['start_cond'] = np.tile(np.array(('A', 'A', 'B', 'B')),
                               int(n_participants / 4))
    print(df)
