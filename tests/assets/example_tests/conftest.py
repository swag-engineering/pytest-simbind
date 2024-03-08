import pytest_simbind

from model import Model


@pytest_simbind.fixture
def model():
    return Model()
