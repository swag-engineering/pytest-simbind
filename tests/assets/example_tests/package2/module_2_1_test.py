import logging
import random

import pytest


@pytest.mark.simbind
def test_2_1_1_single_log(model):
    logging.info("processing test_11")


@pytest.mark.simbind
def test_2_1_2_ten_logs(model):
    for _ in range(10):
        logging.info(f"Current time: {model.time}")
        model.input.EngineRPM = random.randrange(500)
        model.input.Gear = random.randrange(4)
        model.input.TransmissionRPM = random.randrange(1800)
        model.step()
