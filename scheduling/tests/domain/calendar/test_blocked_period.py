from datetime import UTC, datetime

from scheduling.domain.calendar import BlockedPeriod
from scheduling.domain.time import UtcInterval


def test_blocked_period_preserves_utc_interval_and_reason() -> None:
    interval = UtcInterval(
        datetime(2026, 11, 16, 9, tzinfo=UTC), datetime(2026, 11, 16, 10, tzinfo=UTC)
    )

    blocked = BlockedPeriod(interval, reason="Maintenance")

    assert blocked.interval == interval
    assert blocked.reason == "Maintenance"
