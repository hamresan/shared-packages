from datetime import datetime


class TimezoneAwareDatetimeValidator:
    """Validates that timestamps carry timezone information."""

    def validate(self, value: datetime, field_name: str) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{field_name} must be timezone-aware")

    def validate_optional(self, value: datetime | None, field_name: str) -> None:
        if value is not None:
            self.validate(value, field_name)
