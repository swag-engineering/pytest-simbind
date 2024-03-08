import os

import pytest


def fixture(func=None, *, auto_terminate=True):
    if func is not None:
        return craft_fixture(func, auto_terminate=auto_terminate)
    else:
        def decorator_with_args(_func):
            return craft_fixture(_func, auto_terminate=auto_terminate)
        return decorator_with_args


def craft_fixture(func, auto_terminate):
    func._simbind_fixture = True
    func._simbind_parent_pid = os.getpid()
    func._simbind_auto_terminate = auto_terminate
    return pytest.fixture(func)
