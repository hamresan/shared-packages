"""Local working windows anchored to a calendar date."""

from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True, slots=True)
class WorkingWindow:
    """A local window; an end before start continues into the next day."""

    start: time
    end: time

    def __post_init__(self) -> None:
        if self.start.tzinfo is not None or self.end.tzinfo is not None:
            raise ValueError("Working window endpoints must be timezone-naive local times.")
        if self.start == self.end:
            raise ValueError("An equal start and end is not a valid working window.")

    @property
    def crosses_midnight(self) -> bool:
        return self.end < self.start

    def microseconds_from_midnight(self) -> tuple[int, int]:
        """Represent this window on a monotonically increasing local-day axis."""
        start = _time_microseconds(self.start)
        end = _time_microseconds(self.end)
        if self.crosses_midnight:
            end += 86_400_000_000
        return start, end


def _time_microseconds(value: time) -> int:
    return (value.hour * 3600 + value.minute * 60 + value.second) * 1_000_000 + value.microsecond
