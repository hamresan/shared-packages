from datetime import datetime


class TimezoneAwareDatetimeValidator:
    """Validates lifecycle timestamps without normalizing them."""

    def validate(self, value: datetime, field_name: str) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{field_name} must be timezone-aware")
