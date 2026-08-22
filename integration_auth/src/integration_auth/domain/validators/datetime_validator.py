"""Validation for domain datetime values."""

from datetime import datetime


class AwareDateTimeValidator:
    """Require timezone-aware datetimes at domain boundaries."""

    def validate(self, value: datetime, *, field_name: str) -> datetime:
        """Return a timezone-aware datetime or raise ``ValueError``."""
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{field_name} must be timezone-aware")
        return value
