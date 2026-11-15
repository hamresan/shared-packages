"""Clock injection for deterministic testing and host-controlled time."""

from datetime import UTC, datetime


class SystemUtcClock:
    def now(self) -> datetime:
        return datetime.now(UTC)
