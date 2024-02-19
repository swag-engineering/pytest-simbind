import os
import logging
import multiprocessing
from typing import Callable

from .TestLogHandler import TestLogHandler
from .dto import LogMessageDto, TestDataRecordDto, TestUpdateDto, TestStatusDto, TestStateEnum, FailDetailsDto


class DataSink:
    def __init__(
            self,
            function_id: int | str,
            tests_path: str, queue:
            multiprocessing.Queue,
            lock: multiprocessing.Lock,
            finalizer: Callable[[], None] = None
    ):
        self.function_id = function_id
        self.tests_path = tests_path
        self.queue = queue
        self.lock = lock
        self.finalizer = finalizer
        self.log_messages: list[LogMessageDto] = []
        self.handler = TestLogHandler(self.consume_log_message)
        self.handler.setLevel(logging.NOTSET)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.NOTSET)

    def start(self):
        for handler in self.logger.handlers:
            handler.flush()
        self.logger.addHandler(self.handler)

    def stop(self):
        for handler in self.logger.handlers:
            handler.flush()
        self.logger.removeHandler(self.handler)

    def push(self, msg: TestUpdateDto):
        with self.lock:
            self.queue.put(msg)

    def mark_succeed(self):
        if self.finalizer:
            self.finalizer()
        self.push(
            TestUpdateDto(
                test_id=self.function_id,
                data=None,
                status=TestStatusDto(
                    state=TestStateEnum.SUCCEED,
                    fail_details=None
                )
            )
        )
        self.stop()

    def mark_failed(self, exc_type, exc_obj, exc_tb):
        if self.finalizer:
            self.finalizer()
        self.push(
            TestUpdateDto(
                test_id=self.function_id,
                data=None,
                status=TestStatusDto(
                    state=TestStateEnum.FAILED,
                    fail_details=FailDetailsDto(
                        text=str(exc_obj),
                        line_number=exc_tb.tb_frame.f_lineno,
                        file_location=os.path.normpath(
                            os.path.relpath(
                                exc_tb.tb_frame.f_code.co_filename, self.tests_path
                            )
                        )
                    )
                )
            )
        )
        self.stop()

    def consume_log_message(self, record: logging.LogRecord):
        self.log_messages.append(
            LogMessageDto(
                log_level=record.levelno,
                text=record.msg,
                line_number=record.lineno,
                file_location=os.path.normpath(os.path.relpath(record.pathname, self.tests_path))
            )
        )

    def consume_data(self, time: float, inputs: dict[str, float], outputs: dict[str, float]):
        self.push(
            TestUpdateDto(
                test_id=self.function_id,
                data=TestDataRecordDto(
                    timestamp=time,
                    inputs=inputs,
                    outputs=outputs,
                    log_messages=self.log_messages
                ),
                status=None
            )
        )
        self.log_messages = []