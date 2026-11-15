from datetime import UTC, date, datetime, time

import pytest

from scheduling.domain.calendar import (
    BlockedPeriod,
    CalendarException,
    CalendarScope,
    DaySchedule,
    WeeklySchedule,
    WorkingWindow,
)
from scheduling.domain.calendar.revisions import (
    add_blocked_period,
    archive_calendar,
    remove_blocked_period,
    remove_date_exception,
    set_date_exception,
    update_weekly_schedule,
)
from scheduling.domain.time import UtcInterval
from tests.support.calendar_factory import make_calendar


def test_revisions_create_new_immutable_calendar_versions() -> None:
    original = make_calendar(CalendarScope.RESOURCE, "resource-a")
    new_hours = WeeklySchedule((DaySchedule(0, (WorkingWindow(time(10), time(15)),)),))

    revised = update_weekly_schedule(original, new_hours)

    assert original.weekly_schedule != revised.weekly_schedule
    assert original.version == 1
    assert revised.version == 2
    assert revised.calendar_id == original.calendar_id


def test_date_exception_can_be_replaced_and_removed() -> None:
    original = make_calendar(CalendarScope.RESOURCE, "resource-a")
    first = set_date_exception(original, CalendarException(date(2026, 11, 16), closed=True))
    replacement = set_date_exception(
        first,
        CalendarException(
            date(2026, 11, 16), override_windows=(WorkingWindow(time(11), time(13)),)
        ),
    )
    removed = remove_date_exception(replacement, date(2026, 11, 16))

    assert len(first.exceptions) == 1
    assert len(replacement.exceptions) == 1
    assert not replacement.exceptions[0].closed
    assert removed.exceptions == ()
    assert (first.version, replacement.version, removed.version) == (2, 3, 4)


def test_missing_date_exception_cannot_be_removed() -> None:
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")

    with pytest.raises(LookupError):
        remove_date_exception(calendar, date(2026, 11, 16))


def test_blocked_period_can_be_added_and_removed() -> None:
    original = make_calendar(CalendarScope.RESOURCE, "resource-a")
    interval = UtcInterval(
        datetime(2026, 11, 16, 9, tzinfo=UTC), datetime(2026, 11, 16, 10, tzinfo=UTC)
    )
    blocked = BlockedPeriod(interval, "Maintenance")

    added = add_blocked_period(original, blocked)
    removed = remove_blocked_period(added, blocked)

    assert added.blocked_periods == (blocked,)
    assert removed.blocked_periods == ()
    assert removed.version == 3


def test_duplicate_blocked_period_is_rejected() -> None:
    original = make_calendar(CalendarScope.RESOURCE, "resource-a")
    interval = UtcInterval(
        datetime(2026, 11, 16, 9, tzinfo=UTC), datetime(2026, 11, 16, 10, tzinfo=UTC)
    )
    blocked = BlockedPeriod(interval)

    with pytest.raises(ValueError, match="already exists"):
        add_blocked_period(add_blocked_period(original, blocked), blocked)


def test_missing_blocked_period_cannot_be_removed() -> None:
    original = make_calendar(CalendarScope.RESOURCE, "resource-a")
    interval = UtcInterval(
        datetime(2026, 11, 16, 9, tzinfo=UTC), datetime(2026, 11, 16, 10, tzinfo=UTC)
    )

    with pytest.raises(LookupError):
        remove_blocked_period(original, BlockedPeriod(interval))


def test_archive_is_terminal_and_increments_version() -> None:
    original = make_calendar(CalendarScope.RESOURCE, "resource-a")
    archived = archive_calendar(original)

    assert archived.archived
    assert archived.version == 2
    with pytest.raises(ValueError, match="Archived calendars"):
        archive_calendar(archived)
    with pytest.raises(ValueError, match="Archived calendars"):
        set_date_exception(archived, CalendarException(date(2026, 11, 16)))
