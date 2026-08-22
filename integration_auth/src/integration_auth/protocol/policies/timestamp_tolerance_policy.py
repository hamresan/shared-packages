"""Clock-skew tolerance policy for signed request timestamps."""


class TimestampTolerancePolicy:
    """Evaluate whether a request timestamp is within an allowed clock skew."""

    def __init__(self, max_clock_skew_seconds: int) -> None:
        if max_clock_skew_seconds < 0:
            raise ValueError("max_clock_skew_seconds must be non-negative")
        self._max_clock_skew_seconds = max_clock_skew_seconds

    @property
    def max_clock_skew_seconds(self) -> int:
        return self._max_clock_skew_seconds

    def allows(self, *, request_timestamp: int, current_timestamp: int) -> bool:
        if request_timestamp < 0 or current_timestamp < 0:
            return False
        return abs(current_timestamp - request_timestamp) <= self._max_clock_skew_seconds
