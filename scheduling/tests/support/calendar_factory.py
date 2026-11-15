"""Calendar builders for deterministic availability scenarios."""

from datetime import UTC, datetime, time, timedelta

from scheduling.domain.calendar import (
    BlockedPeriod,
    Calendar,
    CalendarException,
    CalendarScope,
    DaySchedule,
    WeeklySchedule,
    WorkingWindow,
)
from scheduling.domain.time import IanaTimeZone, UtcInterval
from scheduling.engine import AvailabilityRequest, BusyInterval


def make_calendar(
    scope: CalendarScope,
    scope_id: str,
    *,
    start: time = time(9),
    end: time = time(17),
    weekday: int = 0,
    timezone_name: str = "Asia/Muscat",
    tenant_id: str = "tenant-a",
    exceptions: tuple[CalendarException, ...] = (),
    blocked_periods: tuple[BlockedPeriod, ...] = (),
) -> Calendar:
    return Calendar(
        calendar_id=f"calendar-{scope_id}",
        tenant_id=tenant_id,
        scope=scope,
        scope_id=scope_id,
        timezone=IanaTimeZone(timezone_name),
        weekly_schedule=WeeklySchedule((DaySchedule(weekday, (WorkingWindow(start, end),)),)),
        exceptions=exceptions,
        blocked_periods=blocked_periods,
    )


def make_request(
    *,
    organization: Calendar | None = None,
    location: Calendar | None = None,
    resources: tuple[Calendar, ...] | None = None,
    duration: timedelta = timedelta(hours=1),
    step: timedelta = timedelta(hours=1),
    now: datetime = datetime(2026, 11, 15, 0, tzinfo=UTC),
    query_window: UtcInterval | None = None,
    busy_intervals: tuple[BusyInterval, ...] = (),
    buffer_before: timedelta = timedelta(),
    buffer_after: timedelta = timedelta(),
    minimum_notice: timedelta = timedelta(),
    maximum_horizon: timedelta = timedelta(days=31),
) -> AvailabilityRequest:
    return AvailabilityRequest(
        organization=organization or make_calendar(CalendarScope.ORGANIZATION, "org-a"),
        location=location or make_calendar(CalendarScope.LOCATION, "location-a"),
        resources=resources
        if resources is not None
        else (make_calendar(CalendarScope.RESOURCE, "resource-a"),),
        query_window=query_window
        or UtcInterval(
            datetime(2026, 11, 16, 0, tzinfo=UTC),
            datetime(2026, 11, 17, 0, tzinfo=UTC),
        ),
        duration=duration,
        step=step,
        now=now,
        busy_intervals=busy_intervals,
        buffer_before=buffer_before,
        buffer_after=buffer_after,
        minimum_notice=minimum_notice,
        maximum_horizon=maximum_horizon,
    )
