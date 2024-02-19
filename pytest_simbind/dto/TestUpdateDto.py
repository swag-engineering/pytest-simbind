from dataclasses import dataclass
from typing import Optional

from .TestDataRecordDto import TestDataRecordDto
from .TestStatusDto import TestStatusDto


@dataclass
class TestUpdateDto:
    test_id: int | str
    data: Optional[TestDataRecordDto]
    status: Optional[TestStatusDto]
