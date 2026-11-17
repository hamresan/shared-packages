from datetime import UTC, datetime

from customer.application.contracts import Clock


class FixedClock(Clock):
    def now(self) -> datetime:
        return datetime(2026, 1, 1, tzinfo=UTC)
