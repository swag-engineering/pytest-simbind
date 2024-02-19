import logging
from typing import Callable


class TestLogHandler(logging.Handler):
    def __init__(self, consumer_callback: Callable[[logging.LogRecord], None]):
        logging.Handler.__init__(self)
        self.callback = consumer_callback

    def emit(self, record):
        self.callback(record)
