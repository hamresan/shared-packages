"""Round-trip every domain configuration field via the persistence schema."""

from datetime import UTC, date, datetime, time

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
from scheduling.infrastructure.persistence.sqlalchemy import CalendarPersistenceMapper


def test_mapper_preserves_all_calendar_fields() -> None:
    calendar = Calendar(
        calendar_id="calendar-a",
        tenant_id="tenant-a",
        scope=CalendarScope.RESOURCE,
        scope_id="resource-a",
        timezone=IanaTimeZone("Europe/London"),
        weekly_schedule=WeeklySchedule(
            (DaySchedule(0, (WorkingWindow(time(23, 15), time(2, 30)),)),)
        ),
        exceptions=(
            CalendarException(date(2026, 12, 25), closed=True),
            CalendarException(date(2026, 12, 26), override_windows=()),
            CalendarException(
                date(2026, 12, 27),
                override_windows=(WorkingWindow(time(10, 30), time(12)),),
            ),
        ),
        annual_closures=(AnnualClosure(1, 1),),
        blocked_periods=(
            BlockedPeriod(
                UtcInterval(
                    datetime(2026, 11, 15, 10, tzinfo=UTC),
                    datetime(2026, 11, 15, 11, tzinfo=UTC),
                ),
                "Maintenance",
            ),
        ),
        version=8,
        archived=True,
    )

    mapper = CalendarPersistenceMapper()

    assert mapper.to_domain(mapper.to_record(calendar)) == calendar
