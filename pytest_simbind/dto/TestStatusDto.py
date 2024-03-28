import enum
from dataclasses import dataclass
from typing import Optional

from .FailDetailsDto import FailDetailsDto


class TestStateEnum(enum.Enum):
    SUCCEED = "SUCCEED"
    FAILED = "FAILED"
    TERMINATED = "TERMINATED"


@dataclass
class TestStatusDto:
    __test__ = False
    state: TestStateEnum
    # exists if state == FAILED
    fail_details: Optional[FailDetailsDto] = None
    # exists if state == TERMINATED
    internal_error: Optional[str] = None
