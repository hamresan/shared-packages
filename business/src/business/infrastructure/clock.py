from datetime import UTC, datetime

from business.application.contracts import Clock


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(UTC)
