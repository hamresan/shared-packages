"""Validate recurring schedules, including overlaps across week boundaries."""

from collections.abc import Iterable

from .window import WorkingWindow

_DAY_MICROSECONDS = 86_400_000_000
_WEEK_MICROSECONDS = 7 * _DAY_MICROSECONDS


def validate_weekly_windows(entries: Iterable[tuple[int, WorkingWindow]]) -> None:
    """Reject two shifts occupying any of the same recurring local wall time."""
    intervals: list[tuple[int, int]] = []
    for weekday, window in entries:
        start, end = window.microseconds_from_midnight()
        lower = weekday * _DAY_MICROSECONDS + start
        upper = weekday * _DAY_MICROSECONDS + end
        intervals.append((lower, upper))

    intervals.sort()
    for previous, current in zip(intervals, intervals[1:], strict=False):
        if previous[1] > current[0]:
            raise ValueError("Recurring working windows may not overlap.")

    if intervals and intervals[-1][1] > intervals[0][0] + _WEEK_MICROSECONDS:
        raise ValueError("Recurring working windows overlap across the week boundary.")


def validate_daily_windows(windows: Iterable[WorkingWindow]) -> None:
    """Reject overlapping date-specific windows anchored to the same local date."""
    intervals = sorted(window.microseconds_from_midnight() for window in windows)
    for previous, current in zip(intervals, intervals[1:], strict=False):
        if previous[1] > current[0]:
            raise ValueError("Date-specific working windows may not overlap.")
