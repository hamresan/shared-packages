"""Pure calendar mutations with version increments and archival invariants."""

from dataclasses import replace
from datetime import date

from .blocked_period import BlockedPeriod
from .calendar import Calendar
from .exception import CalendarException
from .schedule import WeeklySchedule


def update_weekly_schedule(calendar: Calendar, schedule: WeeklySchedule) -> Calendar:
    _ensure_active(calendar)
    return replace(calendar, weekly_schedule=schedule, version=calendar.version + 1)


def set_date_exception(calendar: Calendar, exception: CalendarException) -> Calendar:
    _ensure_active(calendar)
    remaining = tuple(item for item in calendar.exceptions if item.day != exception.day)
    exceptions = tuple(sorted((*remaining, exception), key=lambda item: item.day))
    return replace(calendar, exceptions=exceptions, version=calendar.version + 1)


def remove_date_exception(calendar: Calendar, day: date) -> Calendar:
    _ensure_active(calendar)
    remaining = tuple(item for item in calendar.exceptions if item.day != day)
    if len(remaining) == len(calendar.exceptions):
        raise LookupError("The requested date exception does not exist.")
    return replace(calendar, exceptions=remaining, version=calendar.version + 1)


def add_blocked_period(calendar: Calendar, blocked: BlockedPeriod) -> Calendar:
    _ensure_active(calendar)
    if blocked in calendar.blocked_periods:
        raise ValueError("The blocked period already exists.")
    return replace(
        calendar, blocked_periods=(*calendar.blocked_periods, blocked), version=calendar.version + 1
    )


def remove_blocked_period(calendar: Calendar, blocked: BlockedPeriod) -> Calendar:
    _ensure_active(calendar)
    remaining = tuple(item for item in calendar.blocked_periods if item != blocked)
    if len(remaining) == len(calendar.blocked_periods):
        raise LookupError("The requested blocked period does not exist.")
    return replace(calendar, blocked_periods=remaining, version=calendar.version + 1)


def archive_calendar(calendar: Calendar) -> Calendar:
    _ensure_active(calendar)
    return replace(calendar, archived=True, version=calendar.version + 1)


def _ensure_active(calendar: Calendar) -> None:
    if calendar.archived:
        raise ValueError("Archived calendars cannot be modified.")
