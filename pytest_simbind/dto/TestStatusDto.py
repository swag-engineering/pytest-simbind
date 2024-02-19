import enum
from dataclasses import dataclass
from typing import Optional

from .FailDetailsDto import FailDetailsDto


class TestStateEnum(enum.Enum):
    SUCCEED = "SUCCEED"
    FAILED = "FAILED"


@dataclass
class TestStatusDto:
    state: TestStateEnum
    fail_details: Optional[FailDetailsDto]
