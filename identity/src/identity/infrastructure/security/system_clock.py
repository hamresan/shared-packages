from datetime import UTC, datetime

from identity.application.contracts.security import Clock


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(UTC)
