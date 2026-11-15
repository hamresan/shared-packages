"""Fixed expected slot snapshots, independent of the scheduling algorithm."""

from dataclasses import dataclass, replace
from datetime import UTC, date, datetime, time, timedelta

from scheduling.domain.calendar import (
    AnnualClosure,
    Calendar,
    CalendarException,
    CalendarScope,
    DaySchedule,
    WeeklySchedule,
    WorkingWindow,
)
from scheduling.domain.time import UtcInterval
from scheduling.engine import AvailabilityRequest
from tests.support.calendar_factory import make_calendar, make_request


@dataclass(frozen=True, slots=True)
class GoldenScenario:
    name: str
    request: AvailabilityRequest
    expected: tuple[tuple[str, datetime], ...]


def golden_scenarios() -> tuple[GoldenScenario, ...]:
    morning = make_calendar(CalendarScope.RESOURCE, "morning", end=time(11))
    afternoon = make_calendar(CalendarScope.RESOURCE, "afternoon", start=time(13), end=time(15))
    split = GoldenScenario(
        "independent-resource-shifts",
        make_request(resources=(morning, afternoon)),
        (
            ("morning", _utc(2026, 11, 16, 5)),
            ("morning", _utc(2026, 11, 16, 6)),
            ("afternoon", _utc(2026, 11, 16, 9)),
            ("afternoon", _utc(2026, 11, 16, 10)),
        ),
    )
    closure = GoldenScenario(
        "annual-organization-closure-veto",
        make_request(
            organization=replace(
                make_calendar(CalendarScope.ORGANIZATION, "org-a"),
                annual_closures=(AnnualClosure(11, 16),),
            )
        ),
        (),
    )
    override = GoldenScenario(
        "location-date-override",
        make_request(
            location=make_calendar(
                CalendarScope.LOCATION,
                "location-a",
                exceptions=(
                    CalendarException(
                        date(2026, 11, 16),
                        override_windows=(WorkingWindow(time(10), time(12)),),
                    ),
                ),
            )
        ),
        (
            ("resource-a", _utc(2026, 11, 16, 6)),
            ("resource-a", _utc(2026, 11, 16, 7)),
        ),
    )
    overnight = GoldenScenario(
        "overnight-shift-crossing-utc-date",
        make_request(
            organization=_overnight_calendar(CalendarScope.ORGANIZATION),
            location=_overnight_calendar(CalendarScope.LOCATION),
            resources=(_overnight_calendar(CalendarScope.RESOURCE),),
            now=_utc(2026, 11, 15, 0),
            query_window=UtcInterval(_utc(2026, 11, 16, 17), _utc(2026, 11, 17, 0)),
        ),
        tuple(("resource", _utc(2026, 11, 16, hour)) for hour in (18, 19, 20, 21)),
    )
    buffered = GoldenScenario(
        "buffers-fit-entirely-in-shift",
        make_request(
            resources=(
                make_calendar(CalendarScope.RESOURCE, "resource-a", start=time(10), end=time(12)),
            ),
            step=timedelta(minutes=30),
            buffer_before=timedelta(minutes=30),
            buffer_after=timedelta(minutes=30),
        ),
        (("resource-a", _utc(2026, 11, 16, 6, 30)),),
    )
    return split, closure, override, overnight, buffered


def _utc(year: int, month: int, day: int, hour: int, minute: int = 0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=UTC)


def _overnight_calendar(scope: CalendarScope) -> Calendar:
    original = make_calendar(scope, scope.value)
    return replace(
        original,
        weekly_schedule=WeeklySchedule((DaySchedule(0, (WorkingWindow(time(22), time(2)),)),)),
    )
