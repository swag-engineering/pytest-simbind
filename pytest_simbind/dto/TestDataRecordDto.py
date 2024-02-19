from dataclasses import dataclass

from .LogMessageDto import LogMessageDto


@dataclass
class TestDataRecordDto:
    timestamp: float
    inputs: dict[str, float]
    outputs: dict[str, float]
    log_messages: list[LogMessageDto]
