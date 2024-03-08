import enum
from dataclasses import dataclass
from typing import Optional

from .TestDataRecordDto import TestDataRecordDto
from .TestStatusDto import TestStatusDto


class TestProgressDto(enum.Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"


@dataclass
class TestUpdateDto:
    __test__ = False
    test_id: int | str
    progress: TestProgressDto
    data: Optional[TestDataRecordDto]
    status: Optional[TestStatusDto]
