import os
import subprocess
import sys

import pytest


pytest_plugins = ["pytester"]


@pytest.fixture(scope="session")
def tests_root():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


@pytest.fixture(scope="session")
def assets_path(tests_root):
    return os.path.join(tests_root, "assets")


@pytest.fixture(scope="session")
def example_tests_path(assets_path: str):
    return os.path.join(assets_path, "example_tests")


@pytest.fixture(scope="session")
def model_selector(request, assets_path: str):
    model_type = request.param
    assert model_type != "sil" or model_type != "mock"
    return os.path.join(
        assets_path,
        "model-6.3-py3-none-linux_x86_64.whl" if model_type == "sil" else "model-6.3+mock-py3-none-any.whl"
    )


@pytest.fixture(scope="session", autouse=True)
def install_model(model_selector: str):
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--force-reinstall", "--no-index", model_selector],
        check=True,
        stdout=subprocess.DEVNULL
    )
    yield
    subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", "-y", "model"],
        check=True,
        stdout=subprocess.DEVNULL
    )
