import os
import multiprocessing
from typing import Optional

import pytest
from _pytest.fixtures import FixtureDef, FixtureValue, SubRequest
from _pytest.nodes import Item
from _pytest.runner import runtestprotocol


class SimbindCorePlugin:
    @staticmethod
    def pytest_configure(config):
        config.addinivalue_line(
            "markers",
            "simbind: Marker for functions that utilize simbind fixture",
        )

    @staticmethod
    @pytest.hookimpl(tryfirst=True)
    def pytest_fixture_setup(fixturedef: FixtureDef[FixtureValue], request: SubRequest):
        if hasattr(fixturedef.func, "_simbind_fixture") and \
                getattr(fixturedef.func, "_simbind_parent_pid") == os.getpid():
            pytest.fail(f"Simbind fixture is used within parent process. Try to mark '{request.function.__name__}' "
                        "with '@pytest.mark.simbind'.")

    @staticmethod
    def pytest_runtest_protocol(item: Item, nextitem: Optional[Item]):
        if item.get_closest_marker("simbind"):
            p = multiprocessing.Process(target=runtestprotocol, args=(item, nextitem))
            p.start()
            p.join()
            return True
