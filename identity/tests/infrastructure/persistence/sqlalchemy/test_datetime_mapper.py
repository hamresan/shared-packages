from datetime import UTC, datetime, timedelta, timezone

from identity.infrastructure.persistence.sqlalchemy.datetime_mapper import UtcDateTimeMapper


def test_datetime_mapper_normalizes_naive_and_aware_values_to_utc() -> None:
    mapper = UtcDateTimeMapper()
    naive = datetime(2026, 8, 16, 12, 0, 0)
    plus_four = timezone(timedelta(hours=4))
    aware = datetime(2026, 8, 16, 16, 0, 0, tzinfo=plus_four)

    assert mapper.to_domain(naive) == datetime(2026, 8, 16, 12, 0, 0, tzinfo=UTC)
    assert mapper.to_domain(aware) == datetime(2026, 8, 16, 12, 0, 0, tzinfo=UTC)
    assert mapper.to_domain_optional(None) is None
