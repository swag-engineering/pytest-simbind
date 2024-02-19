from dataclasses import dataclass


@dataclass
class FailDetailsDto:
    text: str
    line_number: int
    file_location: str
