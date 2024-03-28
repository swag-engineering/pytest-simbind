import enum
import logging
from dataclasses import dataclass


class LogLevelEnum(enum.Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


@dataclass
class LogMessageDto:
    log_level: LogLevelEnum
    text: str
    line_number: int
    file_location: str
