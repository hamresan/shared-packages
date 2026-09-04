"""Clock fakes for time-sensitive application tests."""

from datetime import datetime

from instagram_api.application.comments import InstagramReplyClock


class FixedInstagramReplyClock(InstagramReplyClock):
    """Returns a fixed current time for private-reply eligibility tests."""

    def __init__(self, current_time: datetime) -> None:
        self._current_time = current_time

    def now(self) -> datetime:
        return self._current_time
