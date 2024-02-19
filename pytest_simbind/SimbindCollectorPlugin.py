import os
import inspect
import multiprocessing
from typing import Callable
from types import TracebackType

import pytest
from _pytest.nodes import Item
from _pytest.fixtures import FixtureDef, FixtureValue, SubRequest

from .DataSink import DataSink
from .dto import TestCaseInfoDto
from .SimbindCorePlugin import SimbindCorePlugin


class SimbindCollectorPlugin:
    def __init__(
            self,
            tests_path: str,
            queue: multiprocessing.Queue,
            lock: multiprocessing.Lock,
            selector_callback: Callable[[TestCaseInfoDto], int] = None
    ):
        self.tests_path = tests_path
        self.queue = queue
        self.lock = lock
        self.selector_callback = selector_callback
        self.test_cases_map: dict[TestCaseInfoDto, int | str] = {}
        self.data_sink = None

    @staticmethod
    def pytest_configure(config):
        config.pluginmanager.register(SimbindCorePlugin, "pytest_simbind_core")

    def pytest_collection_modifyitems(self, config, items):
        selected = []
        deselected = []
        for item in items:
            test_case = self.item2test_case(item)
            test_id = self.selector_callback(test_case) if self.selector_callback else item.nodeid
            if test_id:
                if test_id in self.test_cases_map.values():
                    raise ValueError(f"Id '{test_id}' already used for test case '{test_case}'")
                self.test_cases_map[item.nodeid] = test_id
                selected.append(item)
            else:
                deselected.append(item)
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected

    @pytest.hookimpl(tryfirst=True)
    def pytest_fixture_setup(self, fixturedef: FixtureDef[FixtureValue], request: SubRequest):
        if hasattr(fixturedef.func, "_simbind_fixture"):
            cache_key = fixturedef.cache_key(request)
            model_obj = fixturedef.func()
            self.data_sink = DataSink(
                self.test_cases_map[request.node.nodeid],
                self.tests_path,
                self.queue,
                self.lock,
                finalizer=model_obj.terminate if getattr(fixturedef.func, "_simbind_auto_terminate") else None
            )
            self.data_sink.start()
            setattr(model_obj, "collector_callback", self.data_sink.consume_data)
            fixturedef.cached_result = (model_obj, cache_key, None)
            return model_obj

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_call(self):
        def retrieve_last_frame(frame: TracebackType):
            if frame.tb_next:
                return retrieve_last_frame(frame.tb_next)
            return frame

        outcome = yield
        if not self.data_sink:
            return
        if outcome.excinfo:
            exc_type, exc_val, exc_tb = outcome.excinfo
            self.data_sink.mark_failed(exc_type, exc_val, retrieve_last_frame(exc_tb))
        else:
            self.data_sink.mark_succeed()

    def pytest_sessionfinish(self):
        self.queue.put(None)

    def item2test_case(self, item: Item) -> TestCaseInfoDto:
        return TestCaseInfoDto(
            node_id=item.nodeid,
            function_name=item.name,
            module_name=inspect.getmodulename(item.parent.name),
            package_path=os.path.relpath(os.path.dirname(item.parent.path), self.tests_path)
        )
