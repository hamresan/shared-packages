from datetime import date, time

import pytest

from scheduling.domain.calendar import CalendarException, WorkingWindow


def test_exception_allows_an_explicit_empty_replacement() -> None:
    exception = CalendarException(date(2026, 11, 16), override_windows=())

    assert exception.override_windows == ()


def test_exception_rejects_closure_with_replacement_windows() -> None:
    with pytest.raises(ValueError):
        CalendarException(date(2026, 11, 16), closed=True, override_windows=())


def test_exception_rejects_overlapping_replacement_windows() -> None:
    with pytest.raises(ValueError, match="overlap"):
        CalendarException(
            date(2026, 11, 16),
            override_windows=(WorkingWindow(time(9), time(12)), WorkingWindow(time(11), time(13))),
        )
