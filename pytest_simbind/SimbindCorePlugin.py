import os
import multiprocessing
from typing import Optional

import pytest
from _pytest.fixtures import FixtureDef, FixtureValue, SubRequest
from _pytest.nodes import Item
from _pytest.reports import pytest_report_to_serializable, pytest_report_from_serializable
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
        def run_test(reports_queue: multiprocessing.Queue, test_item: Item, next_test_item: Optional[Item]):
            reports = runtestprotocol(test_item, log=False, nextitem=next_test_item)
            reports_queue.put([pytest_report_to_serializable(report) for report in reports])
            return True

        if item.get_closest_marker("simbind"):
            queue = multiprocessing.Queue(-1)
            p = multiprocessing.Process(target=run_test, args=(queue, item, nextitem))
            p.start()
            p.join()
            for report_data in queue.get():
                item.ihook.pytest_runtest_logreport(report=pytest_report_from_serializable(report_data))
            return True
