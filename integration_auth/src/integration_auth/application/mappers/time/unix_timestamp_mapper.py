"""Map Unix timestamps to timezone-aware UTC datetimes."""

from datetime import UTC, datetime


class UnixTimestampMapper:
    """Convert validated Unix timestamps to UTC datetime values."""

    def to_datetime(self, timestamp: int) -> datetime:
        if timestamp < 0:
            raise ValueError("timestamp must be non-negative")
        return datetime.fromtimestamp(timestamp, tz=UTC)
