import logging
from typing import Literal
from dataclasses import dataclass


@dataclass
class LogMessageDto:
    log_level: Literal[logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
    text: str
    line_number: int
    file_location: str
