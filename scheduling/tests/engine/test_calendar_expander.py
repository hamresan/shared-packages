from datetime import UTC, date, datetime, time

import pytest

from scheduling.domain.calendar import CalendarException, CalendarScope
from scheduling.domain.time import AmbiguousLocalTimeError, NonexistentLocalTimeError, UtcInterval
from scheduling.engine.calendar_expander import expand_calendar
from tests.support.calendar_factory import make_calendar


def test_expands_normal_overnight_working_window_into_utc() -> None:
    calendar = make_calendar(CalendarScope.RESOURCE, "r1", start=time(22), end=time(2))
    span = UtcInterval(datetime(2026, 11, 16, tzinfo=UTC), datetime(2026, 11, 18, tzinfo=UTC))

    assert expand_calendar(calendar, span) == (
        UtcInterval(datetime(2026, 11, 16, 18, tzinfo=UTC), datetime(2026, 11, 16, 22, tzinfo=UTC)),
    )


def test_hard_closure_blocks_overnight_shift_carryover() -> None:
    calendar = make_calendar(
        CalendarScope.RESOURCE,
        "r1",
        start=time(22),
        end=time(2),
        weekday=6,
        exceptions=(CalendarException(date(2026, 11, 16), closed=True),),
    )
    span = UtcInterval(datetime(2026, 11, 15, tzinfo=UTC), datetime(2026, 11, 17, tzinfo=UTC))

    assert expand_calendar(calendar, span) == (
        UtcInterval(datetime(2026, 11, 15, 18, tzinfo=UTC), datetime(2026, 11, 15, 20, tzinfo=UTC)),
    )


def test_spring_dst_gap_at_window_boundary_is_not_guessed() -> None:
    calendar = make_calendar(
        CalendarScope.RESOURCE,
        "r1",
        start=time(1, 30),
        end=time(3),
        weekday=6,
        timezone_name="Europe/London",
    )
    span = UtcInterval(datetime(2026, 3, 29, tzinfo=UTC), datetime(2026, 3, 30, tzinfo=UTC))

    with pytest.raises(NonexistentLocalTimeError):
        expand_calendar(calendar, span)


def test_ambiguous_dst_window_endpoint_is_not_guessed() -> None:
    calendar = make_calendar(
        CalendarScope.RESOURCE,
        "r1",
        start=time(1, 30),
        end=time(3),
        weekday=6,
        timezone_name="Europe/London",
    )
    span = UtcInterval(datetime(2026, 10, 25, tzinfo=UTC), datetime(2026, 10, 26, tzinfo=UTC))

    with pytest.raises(AmbiguousLocalTimeError):
        expand_calendar(calendar, span)
