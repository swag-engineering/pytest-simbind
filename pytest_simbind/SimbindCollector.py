import os
import asyncio
import inspect
import multiprocessing
from types import TracebackType
from typing import Callable, AsyncIterator

import pytest
from _pytest.nodes import Item
from _pytest.fixtures import FixtureDef, FixtureValue, SubRequest

from .DataSink import DataSink
from .dto import TestCaseInfoDto, TestUpdateDto
from .SimbindCorePlugin import SimbindCorePlugin


class SimbindCollector:
    def __init__(
            self,
            tests_root: str,
            selector_callback: Callable[[TestCaseInfoDto], int | str | None] = None
    ):
        self.tests_root = tests_root
        self.queue = multiprocessing.Queue(-1)
        self.lock = multiprocessing.Lock()
        self.selector_callback = selector_callback
        self.test_cases_map: dict[TestCaseInfoDto, int | str | None] = {}
        self.data_sink = None

    async def start(self, pytest_args: tuple[str] = ()) -> AsyncIterator[TestUpdateDto]:
        async_queue = asyncio.Queue(-1)
        loop = asyncio.get_running_loop()
        # --assert=plain needed to avoid PytestAssertRewriteWarning
        loop.run_in_executor(
            None, lambda: pytest.main(list(pytest_args) + ["--assert=plain", self.tests_root], plugins=[self])
        )
        loop.run_in_executor(None, self.redirect_to_to_async_queue, async_queue, loop)
        while True:
            msg = await async_queue.get()
            if msg is None:
                break
            yield msg

    def redirect_to_to_async_queue(self, async_queue: asyncio.Queue, loop: asyncio.AbstractEventLoop):
        while True:
            msg = self.queue.get()
            if msg is None:
                asyncio.run_coroutine_threadsafe(async_queue.put(None), loop)
                break
            asyncio.run_coroutine_threadsafe(async_queue.put(msg), loop)

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
                self.tests_root,
                self.queue,
                self.lock,
                finalizer=model_obj.terminate if getattr(fixturedef.func, "_simbind_auto_terminate") else None
            )
            self.data_sink.start()
            # TODO should raise error if collector_callback doesn't exist?
            # e.g. simbind fixture used on non-simbind object
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
            package_path=os.path.relpath(os.path.dirname(item.parent.path), self.tests_root)
        )
