"""Replay-window retention policy."""


class ReplayWindowPolicy:
    """Keep consumed nonces long enough to prevent valid-request replay."""

    def __init__(self, retention_seconds: int) -> None:
        if retention_seconds <= 0:
            raise ValueError("retention_seconds must be positive")
        self._retention_seconds = retention_seconds

    @property
    def retention_seconds(self) -> int:
        return self._retention_seconds

    def nonce_expires_at(
        self,
        *,
        request_timestamp: int,
        current_timestamp: int,
        max_clock_skew_seconds: int,
    ) -> int:
        """Return the minimum safe expiry for a consumed nonce."""
        if request_timestamp < 0 or current_timestamp < 0 or max_clock_skew_seconds < 0:
            raise ValueError("timestamps and max_clock_skew_seconds must be non-negative")

        latest_accepted_timestamp = request_timestamp + max_clock_skew_seconds
        retention_deadline = current_timestamp + self._retention_seconds
        return max(latest_accepted_timestamp, retention_deadline)
