from datetime import UTC, datetime

import pytest
from sqlalchemy.dialects.sqlite import dialect as sqlite_dialect

from instagram_auth.infrastructure.persistence.types import UtcDateTime


def test_utc_datetime_rejects_naive_values() -> None:
    with pytest.raises(ValueError, match="Timezone-aware"):
        UtcDateTime().process_bind_param(datetime(2026, 9, 3), sqlite_dialect())


def test_utc_datetime_restores_timezone_for_sqlite_values() -> None:
    value = UtcDateTime().process_result_value(datetime(2026, 9, 3, 10, 0), sqlite_dialect())

    assert value == datetime(2026, 9, 3, 10, 0, tzinfo=UTC)
