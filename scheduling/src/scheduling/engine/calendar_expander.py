"""Expand local recurring calendar rules into absolute UTC working intervals."""

from datetime import UTC, date, datetime, timedelta

from scheduling.domain.calendar import Calendar, WorkingWindow
from scheduling.domain.time import UtcInterval, resolve_local_datetime

from .intervals import merge_intervals, subtract_intervals


def expand_calendar(calendar: Calendar, window: UtcInterval) -> tuple[UtcInterval, ...]:
    """Expand an explicit calendar, applying hard closures to overnight carryovers."""
    zoneinfo = calendar.timezone.to_zoneinfo()
    first_day = window.start.astimezone(zoneinfo).date() - timedelta(days=1)
    last_day = window.end.astimezone(zoneinfo).date()

    intervals: list[UtcInterval] = []
    closures: list[UtcInterval] = []
    day = first_day
    while day <= last_day:
        for working_window in calendar.windows_for(day):
            interval = _expand_working_window(day, working_window, calendar)
            if interval.overlaps(window):
                intervals.append(interval)
        if calendar.is_closed(day):
            closures.append(_closed_local_day(day, calendar))
        day += timedelta(days=1)

    return subtract_intervals(merge_intervals(intervals), closures)


def _expand_working_window(day: date, window: WorkingWindow, calendar: Calendar) -> UtcInterval:
    end_day = day + timedelta(days=1) if window.crosses_midnight else day
    local_start = resolve_local_datetime(day, window.start, calendar.timezone)
    local_end = resolve_local_datetime(end_day, window.end, calendar.timezone)
    return UtcInterval(local_start.astimezone(UTC), local_end.astimezone(UTC))


def _closed_local_day(day: date, calendar: Calendar) -> UtcInterval:
    next_day = day + timedelta(days=1)
    midnight = datetime.min.time()
    start = resolve_local_datetime(day, midnight, calendar.timezone)
    end = resolve_local_datetime(next_day, midnight, calendar.timezone)
    return UtcInterval(start.astimezone(UTC), end.astimezone(UTC))
