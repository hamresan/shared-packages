from dataclasses import replace
from datetime import date, time

import pytest

from scheduling.domain.calendar import (
    AnnualClosure,
    Calendar,
    CalendarException,
    CalendarScope,
    DaySchedule,
    WeeklySchedule,
    WorkingWindow,
)
from scheduling.domain.time import IanaTimeZone


def make_calendar(
    *,
    exceptions: tuple[CalendarException, ...] = (),
    annual_closures: tuple[AnnualClosure, ...] = (),
) -> Calendar:
    return Calendar(
        calendar_id="calendar-a",
        tenant_id="tenant-a",
        scope=CalendarScope.RESOURCE,
        scope_id="resource-a",
        timezone=IanaTimeZone("Asia/Muscat"),
        weekly_schedule=WeeklySchedule((DaySchedule(0, (WorkingWindow(time(9), time(17)),)),)),
        exceptions=exceptions,
        annual_closures=annual_closures,
    )


def test_calendar_date_override_replaces_regular_weekly_hours() -> None:
    replacement = (WorkingWindow(time(12), time(15)),)
    calendar = make_calendar(
        exceptions=(CalendarException(date(2026, 11, 16), override_windows=replacement),)
    )

    assert calendar.windows_for(date(2026, 11, 16)) == replacement


def test_calendar_explicit_closed_date_has_no_working_windows() -> None:
    calendar = make_calendar(exceptions=(CalendarException(date(2026, 11, 16), closed=True),))

    assert calendar.windows_for(date(2026, 11, 16)) == ()


def test_annual_closure_wins_over_same_date_replacement() -> None:
    calendar = make_calendar(
        exceptions=(
            CalendarException(
                date(2026, 11, 16), override_windows=(WorkingWindow(time(12), time(15)),)
            ),
        ),
        annual_closures=(AnnualClosure(11, 16),),
    )

    assert calendar.windows_for(date(2026, 11, 16)) == ()


def test_calendar_rejects_multiple_exceptions_for_the_same_day() -> None:
    with pytest.raises(ValueError, match="only one"):
        make_calendar(
            exceptions=(
                CalendarException(date(2026, 11, 16)),
                CalendarException(date(2026, 11, 16), closed=True),
            )
        )


def test_calendar_rejects_empty_scope_identifiers() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        Calendar(
            calendar_id="calendar-a",
            tenant_id=" ",
            scope=CalendarScope.RESOURCE,
            scope_id="resource-a",
            timezone=IanaTimeZone("UTC"),
            weekly_schedule=WeeklySchedule(),
        )


def test_archived_calendar_exposes_no_working_hours() -> None:
    calendar = replace(make_calendar(), archived=True)

    assert calendar.windows_for(date(2026, 11, 16)) == ()


def test_calendar_version_must_be_positive() -> None:
    with pytest.raises(ValueError, match="version"):
        replace(make_calendar(), version=0)


def test_calendar_identity_is_required() -> None:
    with pytest.raises(ValueError, match="identifiers"):
        replace(make_calendar(), calendar_id="")
