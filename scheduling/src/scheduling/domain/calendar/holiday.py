"""Recurring annual closures without imposing a country-specific holiday calendar."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class AnnualClosure:
    month: int
    day: int

    def __post_init__(self) -> None:
        if isinstance(self.month, bool) or isinstance(self.day, bool):
            raise ValueError("Month and day must be integers.")
        date(2024, self.month, self.day)

    def matches(self, candidate: date) -> bool:
        return self.month == candidate.month and self.day == candidate.day
