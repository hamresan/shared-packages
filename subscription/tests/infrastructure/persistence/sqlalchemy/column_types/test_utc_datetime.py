from datetime import UTC, datetime, timedelta, timezone

import pytest
from sqlalchemy.dialects.sqlite import dialect as sqlite_dialect

from subscription.infrastructure.persistence.sqlalchemy.column_types import UtcDateTime


def test_utc_datetime_rejects_naive_values() -> None:
    column_type = UtcDateTime()

    with pytest.raises(ValueError, match="timezone-aware"):
        column_type.process_bind_param(datetime(2026, 8, 22, 7, 0), sqlite_dialect())


def test_utc_datetime_normalizes_bound_values_to_utc() -> None:
    column_type = UtcDateTime()
    source = datetime(2026, 8, 22, 11, 0, tzinfo=timezone(timedelta(hours=4)))

    result = column_type.process_bind_param(source, sqlite_dialect())

    assert result == datetime(2026, 8, 22, 7, 0, tzinfo=UTC)
    assert result is not None
    assert result.tzinfo is UTC


def test_utc_datetime_restores_timezone_after_sqlite_round_trip() -> None:
    column_type = UtcDateTime()
    sqlite_value = datetime(2026, 8, 22, 7, 0)

    result = column_type.process_result_value(sqlite_value, sqlite_dialect())

    assert result == datetime(2026, 8, 22, 7, 0, tzinfo=UTC)
    assert result is not None
    assert result.tzinfo is UTC
