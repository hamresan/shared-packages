from datetime import UTC, datetime


class UtcDateTimeMapper:
    """Normalize database datetimes to timezone-aware UTC values."""

    def to_domain(self, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
