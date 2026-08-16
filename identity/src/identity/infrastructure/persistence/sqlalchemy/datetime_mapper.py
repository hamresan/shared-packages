from datetime import UTC, datetime


class UtcDateTimeMapper:
    def to_domain(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    def to_domain_optional(self, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return self.to_domain(value)
