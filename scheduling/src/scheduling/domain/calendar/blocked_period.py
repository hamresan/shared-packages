"""An unavailable interval with an optional human-readable reason."""

from dataclasses import dataclass

from scheduling.domain.time import UtcInterval


@dataclass(frozen=True, slots=True)
class BlockedPeriod:
    interval: UtcInterval
    reason: str | None = None
