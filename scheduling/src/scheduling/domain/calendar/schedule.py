"""Immutable weekday-to-working-window mapping."""

from dataclasses import dataclass
from datetime import date

from .schedule_validator import validate_daily_windows, validate_weekly_windows
from .window import WorkingWindow


@dataclass(frozen=True, slots=True)
class DaySchedule:
    weekday: int
    windows: tuple[WorkingWindow, ...]

    def __post_init__(self) -> None:
        if isinstance(self.weekday, bool) or not 0 <= self.weekday <= 6:
            raise ValueError("Weekday must be an integer from 0 (Monday) to 6 (Sunday).")
        validate_daily_windows(self.windows)


@dataclass(frozen=True, slots=True)
class WeeklySchedule:
    days: tuple[DaySchedule, ...] = ()

    def __post_init__(self) -> None:
        weekdays = [day.weekday for day in self.days]
        if len(weekdays) != len(set(weekdays)):
            raise ValueError("A weekday may appear only once in a weekly schedule.")
        validate_weekly_windows(
            (day.weekday, window) for day in self.days for window in day.windows
        )

    def windows_for(self, day: date) -> tuple[WorkingWindow, ...]:
        for schedule in self.days:
            if schedule.weekday == day.weekday():
                return schedule.windows
        return ()
