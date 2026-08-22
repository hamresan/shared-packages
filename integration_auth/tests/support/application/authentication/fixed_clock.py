"""Fixed clock for authentication tests."""

from integration_auth.application.contracts.authentication.clock import Clock


class FixedClock(Clock):
    """Return one deterministic Unix timestamp."""

    def __init__(self, timestamp: int) -> None:
        self._timestamp = timestamp

    def now_timestamp(self) -> int:
        return self._timestamp
