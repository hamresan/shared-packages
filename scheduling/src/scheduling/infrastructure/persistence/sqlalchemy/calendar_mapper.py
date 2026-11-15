"""Explicit conversion between domain snapshots and persistence values."""

from datetime import UTC, date, datetime, time
from typing import Any

from scheduling.domain.calendar import (
    AnnualClosure,
    BlockedPeriod,
    Calendar,
    CalendarException,
    CalendarScope,
    DaySchedule,
    WeeklySchedule,
    WorkingWindow,
)
from scheduling.domain.time import IanaTimeZone, UtcInterval

from .calendar_record import CalendarRecord


class CalendarPersistenceMapper:
    """Keep JSON layout and reconstruction separate from query orchestration."""

    def to_record(self, calendar: Calendar) -> CalendarRecord:
        return CalendarRecord(**self.to_values(calendar))

    def to_values(self, calendar: Calendar) -> dict[str, Any]:
        return {
            "calendar_id": calendar.calendar_id,
            "tenant_id": calendar.tenant_id,
            "scope": calendar.scope.value,
            "scope_id": calendar.scope_id,
            "timezone_name": calendar.timezone.key,
            "weekly_schedule": {
                "days": [
                    {"weekday": day.weekday, "windows": self._windows(day.windows)}
                    for day in calendar.weekly_schedule.days
                ]
            },
            "exceptions": [
                {
                    "day": exception.day.isoformat(),
                    "closed": exception.closed,
                    "override_windows": (
                        None
                        if exception.override_windows is None
                        else self._windows(exception.override_windows)
                    ),
                }
                for exception in calendar.exceptions
            ],
            "annual_closures": [
                {"month": holiday.month, "day": holiday.day} for holiday in calendar.annual_closures
            ],
            "blocked_periods": [
                {
                    "start": block.interval.start.isoformat(),
                    "end": block.interval.end.isoformat(),
                    "reason": block.reason,
                }
                for block in calendar.blocked_periods
            ],
            "version": calendar.version,
            "archived": calendar.archived,
        }

    def to_domain(self, record: CalendarRecord) -> Calendar:
        return Calendar(
            calendar_id=record.calendar_id,
            tenant_id=record.tenant_id,
            scope=CalendarScope(record.scope),
            scope_id=record.scope_id,
            timezone=IanaTimeZone(record.timezone_name),
            weekly_schedule=WeeklySchedule(
                tuple(
                    DaySchedule(
                        weekday=day["weekday"],
                        windows=self._restore_windows(day["windows"]),
                    )
                    for day in record.weekly_schedule["days"]
                )
            ),
            exceptions=tuple(
                CalendarException(
                    day=date.fromisoformat(exception["day"]),
                    closed=exception["closed"],
                    override_windows=(
                        None
                        if exception["override_windows"] is None
                        else self._restore_windows(exception["override_windows"])
                    ),
                )
                for exception in record.exceptions
            ),
            annual_closures=tuple(
                AnnualClosure(month=closure["month"], day=closure["day"])
                for closure in record.annual_closures
            ),
            blocked_periods=tuple(
                BlockedPeriod(
                    interval=UtcInterval(
                        datetime.fromisoformat(block["start"]).astimezone(UTC),
                        datetime.fromisoformat(block["end"]).astimezone(UTC),
                    ),
                    reason=block["reason"],
                )
                for block in record.blocked_periods
            ),
            version=record.version,
            archived=record.archived,
        )

    @staticmethod
    def _windows(windows: tuple[WorkingWindow, ...]) -> list[dict[str, str]]:
        return [
            {"start": window.start.isoformat(), "end": window.end.isoformat()} for window in windows
        ]

    @staticmethod
    def _restore_windows(values: list[dict[str, str]]) -> tuple[WorkingWindow, ...]:
        return tuple(
            WorkingWindow(time.fromisoformat(value["start"]), time.fromisoformat(value["end"]))
            for value in values
        )
