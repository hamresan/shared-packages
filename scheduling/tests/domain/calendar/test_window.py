from datetime import UTC, time

import pytest

from scheduling.domain.calendar import WorkingWindow


def test_overnight_window_spans_the_following_local_day() -> None:
    window = WorkingWindow(time(22), time(2))

    assert window.crosses_midnight
    assert window.microseconds_from_midnight() == (79_200_000_000, 93_600_000_000)


def test_daytime_window_does_not_cross_midnight() -> None:
    assert not WorkingWindow(time(9), time(17)).crosses_midnight


def test_subsecond_window_preserves_exact_microsecond_precision() -> None:
    window = WorkingWindow(time(9, 0, 0, 1), time(9, 0, 0, 2))

    start, end = window.microseconds_from_midnight()
    assert end - start == 1


@pytest.mark.parametrize(
    ("start", "end"),
    [(time(9), time(9)), (time(9, tzinfo=UTC), time(10))],
)
def test_working_window_rejects_invalid_local_times(start: time, end: time) -> None:
    with pytest.raises(ValueError):
        WorkingWindow(start, end)
