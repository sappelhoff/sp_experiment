"""Testing the utility functions."""
from sp_experiment.utils import (Fake_serial)


def test_Fake_serial():
    ser = Fake_serial()
    ser.write(1)
    assert True
