from dataclasses import dataclass


@dataclass
class FailDetailsDto:
    exc_type: str
    text: str
    line_number: int
    file_location: str
