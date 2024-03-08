import random

import pytest


@pytest.mark.simbind
def test_1_1_1_non_zero_input(model):
    model.input.EngineRPM = random.randrange(1, 3500)
    model.input.Gear = random.randrange(1, 3)
    model.input.TransmissionRPM = random.randrange(1, 2100)


@pytest.mark.simbind
def test_1_1_2_ten_steps(model):
    for _ in range(10):
        model.input.EngineRPM = random.randrange(500)
        model.input.Gear = random.randrange(4)
        model.input.TransmissionRPM = random.randrange(1800)
        model.step()
