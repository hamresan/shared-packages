from datetime import datetime

from business.application.contracts import Clock


class FixedClock(Clock):
    def __init__(self, current_time: datetime) -> None:
        self._current_time = current_time

    def now(self) -> datetime:
        return self._current_time
