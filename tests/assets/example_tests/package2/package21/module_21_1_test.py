import time
import logging

import pytest


@pytest.mark.simbind
def test_21_1_1_realistic(model):
    logging.info("processing test_21_1_1_realistic")
    model.input.EngineRPM = 3500
    model.input.Gear = 3
    model.input.TransmissionRPM = 2000
    while model.time < 0.1:
        model.step()
    assert False, "Something went wrong"


@pytest.mark.simbind
def test_21_1_2_exception(model):
    raise ValueError("Something went wrong")
