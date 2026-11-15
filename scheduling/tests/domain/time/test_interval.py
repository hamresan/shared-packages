from datetime import UTC, datetime, timedelta, timezone

import pytest

from scheduling.domain.time import InvalidIntervalError, UtcInterval


def utc(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 11, 15, hour, minute, tzinfo=UTC)


def test_interval_accepts_utc_instants_and_keeps_half_open_bounds() -> None:
    interval = UtcInterval(utc(9), utc(10))

    assert interval.start == utc(9)
    assert interval.end == utc(10)
    assert interval.overlaps(UtcInterval(utc(9, 30), utc(10, 30)))
    assert not interval.overlaps(UtcInterval(utc(10), utc(11)))


def test_interval_contains_another_complete_interval() -> None:
    interval = UtcInterval(utc(9), utc(12))

    assert interval.contains(UtcInterval(utc(9), utc(12)))
    assert interval.contains(UtcInterval(utc(10), utc(11)))
    assert not interval.contains(UtcInterval(utc(11), utc(13)))


@pytest.mark.parametrize(
    ("start", "end"),
    [
        (utc(9), utc(9)),
        (utc(11), utc(10)),
        (datetime(2026, 11, 15, 9), utc(10)),
        (utc(9), datetime(2026, 11, 15, 10)),
        (utc(9).astimezone(timezone(timedelta(hours=4))), utc(10)),
    ],
)
def test_interval_rejects_invalid_bounds(start: datetime, end: datetime) -> None:
    with pytest.raises(InvalidIntervalError):
        UtcInterval(start, end)
