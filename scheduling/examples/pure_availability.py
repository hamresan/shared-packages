"""Standalone availability calculation without databases or web frameworks."""

from datetime import UTC, datetime, time, timedelta

from scheduling.domain.calendar import (
    Calendar,
    CalendarScope,
    DaySchedule,
    WeeklySchedule,
    WorkingWindow,
)
from scheduling.domain.time import IanaTimeZone, UtcInterval
from scheduling.engine import (
    AvailabilityRequest,
    AvailableSlot,
    BusyInterval,
    calculate_availability,
)


def build_calendar(scope: CalendarScope, scope_id: str, start: time, end: time) -> Calendar:
    """Create a Monday-only calendar in the Muscat timezone."""
    return Calendar(
        calendar_id=f"calendar-{scope_id}",
        tenant_id="demo-tenant",
        scope=scope,
        scope_id=scope_id,
        timezone=IanaTimeZone("Asia/Muscat"),
        weekly_schedule=WeeklySchedule(
            (DaySchedule(0, (WorkingWindow(start, end),)),)
        ),
    )


def calculate_demo_slots() -> tuple[AvailableSlot, ...]:
    """Intersect organization, location, and resource calendars with an external booking."""
    organization = build_calendar(CalendarScope.ORGANIZATION, "org-1", time(9), time(17))
    location = build_calendar(CalendarScope.LOCATION, "location-1", time(9), time(17))
    morning = build_calendar(CalendarScope.RESOURCE, "staff-a", time(9), time(11))
    afternoon = build_calendar(CalendarScope.RESOURCE, "staff-b", time(13), time(15))

    request = AvailabilityRequest(
        organization=organization,
        location=location,
        resources=(morning, afternoon),
        query_window=UtcInterval(
            datetime(2026, 11, 16, tzinfo=UTC),
            datetime(2026, 11, 17, tzinfo=UTC),
        ),
        duration=timedelta(minutes=30),
        step=timedelta(minutes=30),
        now=datetime(2026, 11, 15, tzinfo=UTC),
        busy_intervals=(
            BusyInterval(
                "staff-a",
                UtcInterval(
                    datetime(2026, 11, 16, 5, 30, tzinfo=UTC),
                    datetime(2026, 11, 16, 6, tzinfo=UTC),
                ),
            ),
        ),
    )
    return calculate_availability(request)


def main() -> None:
    for slot in calculate_demo_slots():
        print(slot.resource_id, slot.interval.start.isoformat(), slot.interval.end.isoformat())


if __name__ == "__main__":
    main()
