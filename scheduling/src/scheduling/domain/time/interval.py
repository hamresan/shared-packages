"""Half-open UTC intervals used for overlap calculations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from .errors import InvalidIntervalError


@dataclass(frozen=True, slots=True)
class UtcInterval:
    """Represent a non-empty [start, end) interval of absolute UTC instants."""

    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        for name, value in (("start", self.start), ("end", self.end)):
            if value.tzinfo is None or value.utcoffset() != timedelta(0):
                raise InvalidIntervalError(f"{name} must be a timezone-aware UTC datetime.")

        start = self.start.astimezone(UTC)
        end = self.end.astimezone(UTC)
        if start >= end:
            raise InvalidIntervalError("An interval must have start < end.")

        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)

    def overlaps(self, other: UtcInterval) -> bool:
        """Adjacent half-open intervals do not overlap."""
        return self.start < other.end and other.start < self.end

    def contains(self, other: UtcInterval) -> bool:
        """Return whether another interval fits completely within this interval."""
        return self.start <= other.start and other.end <= self.end
