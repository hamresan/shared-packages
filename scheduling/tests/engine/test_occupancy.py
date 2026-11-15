from datetime import UTC, datetime, timedelta

from scheduling.domain.time import UtcInterval
from scheduling.engine.occupancy import occupied_window


def test_occupancy_includes_both_buffers() -> None:
    slot = UtcInterval(
        datetime(2026, 11, 16, 9, tzinfo=UTC), datetime(2026, 11, 16, 10, tzinfo=UTC)
    )

    assert occupied_window(slot, timedelta(minutes=15), timedelta(minutes=30)) == UtcInterval(
        datetime(2026, 11, 16, 8, 45, tzinfo=UTC),
        datetime(2026, 11, 16, 10, 30, tzinfo=UTC),
    )
