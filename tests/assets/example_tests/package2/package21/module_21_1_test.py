import time
import logging

import pytest


@pytest.mark.simbind
def test_21_1_1_realistic(model):
    logging.info("processing test_21_1_1_realistic")
    model.input.EngineRPM = 3500
    model.input.Gear = 3
    model.input.TransmissionRPM = 2000
    model.step()
    while model.time < 0.1:
        assert model.Ti < 10


@pytest.mark.simbind
def test_21_1_2_with_delays(model):
    for _ in range(10):
        time.sleep(0.5)
        model.step()
