"""Fixed-size realistic resource pools with independent shifts and busy intervals."""

from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta

from scheduling.domain.calendar import (
    Calendar,
    CalendarScope,
    DaySchedule,
    WeeklySchedule,
    WorkingWindow,
)
from scheduling.domain.time import IanaTimeZone, UtcInterval
from scheduling.engine import AvailabilityRequest, BusyInterval


@dataclass(frozen=True, slots=True)
class BenchmarkSize:
    resources: int
    days: int

    def __post_init__(self) -> None:
        if not 1 <= self.resources <= 100 or not 1 <= self.days <= 31:
            raise ValueError("Benchmark sizes must fit within public query limits.")


def make_benchmark_request(size: BenchmarkSize) -> AvailabilityRequest:
    """Every resource has an independent half-day shift and one busy slot per day."""
    start = datetime(2026, 11, 16, tzinfo=UTC)
    resources = tuple(
        _benchmark_calendar(
            CalendarScope.RESOURCE,
            f"resource-{index:03d}",
            time(9) if index % 2 == 0 else time(13),
            time(13) if index % 2 == 0 else time(17),
        )
        for index in range(size.resources)
    )
    busy = tuple(
        BusyInterval(
            resource.scope_id,
            UtcInterval(
                start + timedelta(days=day, hours=6 if index % 2 == 0 else 10),
                start + timedelta(days=day, hours=6 if index % 2 == 0 else 10, minutes=30),
            ),
        )
        for index, resource in enumerate(resources)
        for day in range(size.days)
    )
    return AvailabilityRequest(
        organization=_benchmark_calendar(CalendarScope.ORGANIZATION, "org-1", time(9), time(17)),
        location=_benchmark_calendar(CalendarScope.LOCATION, "location-1", time(9), time(17)),
        resources=resources,
        query_window=UtcInterval(start, start + timedelta(days=size.days)),
        duration=timedelta(minutes=30),
        step=timedelta(minutes=15),
        now=start,
        buffer_before=timedelta(minutes=15),
        buffer_after=timedelta(minutes=15),
        busy_intervals=busy,
    )


def _benchmark_calendar(scope: CalendarScope, scope_id: str, first: time, last: time) -> Calendar:
    weekdays = tuple(DaySchedule(day, (WorkingWindow(first, last),)) for day in range(7))
    return Calendar(
        calendar_id=f"calendar-{scope_id}",
        tenant_id="benchmark-tenant",
        scope=scope,
        scope_id=scope_id,
        timezone=IanaTimeZone("Asia/Muscat"),
        weekly_schedule=WeeklySchedule(weekdays),
    )
