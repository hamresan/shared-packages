from datetime import datetime


class TimestampOrderValidator:
    """Validates ordering relationships between optional timestamps."""

    def ensure_not_before(
        self,
        value: datetime | None,
        minimum: datetime,
        field_name: str,
        minimum_field_name: str,
    ) -> None:
        if value is not None and value < minimum:
            raise ValueError(f"{field_name} must not be before {minimum_field_name}")

    def ensure_after(
        self,
        value: datetime | None,
        minimum: datetime | None,
        field_name: str,
        minimum_field_name: str,
    ) -> None:
        if value is not None and minimum is not None and value <= minimum:
            raise ValueError(f"{field_name} must be after {minimum_field_name}")
