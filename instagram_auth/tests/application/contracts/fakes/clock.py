from datetime import datetime

from instagram_auth.application.contracts import Clock


class FixedClock(Clock):
    """Deterministic clock fake for application tests."""

    def __init__(self, current_time: datetime) -> None:
        self.current_time = current_time

    def now(self) -> datetime:
        return self.current_time
