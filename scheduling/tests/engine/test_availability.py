from dataclasses import replace
from datetime import UTC, date, datetime, time, timedelta

from scheduling.domain.calendar import (
    BlockedPeriod,
    CalendarException,
    CalendarScope,
    WorkingWindow,
)
from scheduling.domain.time import UtcInterval
from scheduling.engine import BusyInterval, calculate_availability
from tests.support.calendar_factory import make_calendar, make_request


def test_resource_specific_schedules_are_not_shared_across_the_pool() -> None:
    first = make_calendar(CalendarScope.RESOURCE, "a", start=time(9), end=time(11))
    second = make_calendar(CalendarScope.RESOURCE, "b", start=time(13), end=time(15))

    result = calculate_availability(make_request(resources=(first, second)))

    assert [(slot.resource_id, slot.interval.start.hour) for slot in result] == [
        ("a", 5),
        ("a", 6),
        ("b", 9),
        ("b", 10),
    ]


def test_organization_closure_cannot_be_overridden_by_resource_hours() -> None:
    organization = make_calendar(
        CalendarScope.ORGANIZATION,
        "org-a",
        exceptions=(CalendarException(date(2026, 11, 16), closed=True),),
    )
    resource = make_calendar(
        CalendarScope.RESOURCE,
        "resource-a",
        exceptions=(
            CalendarException(
                date(2026, 11, 16),
                override_windows=(
                    # An explicitly open resource cannot reopen the closed organization.
                    WorkingWindow(time(9), time(17)),
                ),
            ),
        ),
    )

    assert (
        calculate_availability(make_request(organization=organization, resources=(resource,))) == ()
    )


def test_location_closure_cannot_be_overridden_by_resource_hours() -> None:
    location = make_calendar(
        CalendarScope.LOCATION,
        "location-a",
        exceptions=(CalendarException(date(2026, 11, 16), closed=True),),
    )

    assert calculate_availability(make_request(location=location)) == ()


def test_full_buffer_must_fit_inside_all_applicable_working_windows() -> None:
    resource = make_calendar(CalendarScope.RESOURCE, "resource-a", start=time(10), end=time(12))
    request = make_request(
        resources=(resource,),
        buffer_before=timedelta(minutes=30),
        buffer_after=timedelta(minutes=30),
        step=timedelta(minutes=30),
    )

    result = calculate_availability(request)

    assert [slot.interval.start for slot in result] == [datetime(2026, 11, 16, 6, 30, tzinfo=UTC)]


def test_busy_intervals_and_resource_blocked_periods_exclude_occupied_time() -> None:
    resource = make_calendar(
        CalendarScope.RESOURCE,
        "resource-a",
        start=time(9),
        end=time(12),
        blocked_periods=(
            BlockedPeriod(
                UtcInterval(
                    datetime(2026, 11, 16, 7, tzinfo=UTC),
                    datetime(2026, 11, 16, 8, tzinfo=UTC),
                )
            ),
        ),
    )
    request = make_request(
        resources=(resource,),
        busy_intervals=(
            BusyInterval(
                "resource-a",
                UtcInterval(
                    datetime(2026, 11, 16, 5, tzinfo=UTC), datetime(2026, 11, 16, 6, tzinfo=UTC)
                ),
            ),
        ),
    )

    assert [slot.interval.start.hour for slot in calculate_availability(request)] == [6]


def test_minimum_notice_and_maximum_horizon_filter_slots_deterministically() -> None:
    request = make_request(
        now=datetime(2026, 11, 16, 5, tzinfo=UTC),
        minimum_notice=timedelta(hours=2),
        maximum_horizon=timedelta(hours=4),
    )

    assert [slot.interval.start.hour for slot in calculate_availability(request)] == [7, 8]


def test_repeated_calculations_from_identical_snapshots_are_identical() -> None:
    request = make_request()

    assert calculate_availability(request) == calculate_availability(request)


def test_organization_blocked_period_excludes_every_resource() -> None:
    blocked = UtcInterval(
        datetime(2026, 11, 16, 5, tzinfo=UTC), datetime(2026, 11, 16, 6, tzinfo=UTC)
    )
    organization = make_calendar(
        CalendarScope.ORGANIZATION, "org-a", blocked_periods=(BlockedPeriod(blocked),)
    )

    starts = [
        slot.interval.start.hour
        for slot in calculate_availability(make_request(organization=organization))
    ]

    assert 5 not in starts
    assert 6 in starts


def test_fall_dst_transition_produces_distinct_utc_slots_for_repeated_hour() -> None:
    organization = make_calendar(
        CalendarScope.ORGANIZATION,
        "org-a",
        start=time(0),
        end=time(3),
        weekday=6,
        timezone_name="Europe/London",
    )
    location = make_calendar(
        CalendarScope.LOCATION,
        "location-a",
        start=time(0),
        end=time(3),
        weekday=6,
        timezone_name="Europe/London",
    )
    resource = make_calendar(
        CalendarScope.RESOURCE,
        "resource-a",
        start=time(0),
        end=time(3),
        weekday=6,
        timezone_name="Europe/London",
    )
    request = make_request(
        organization=organization,
        location=location,
        resources=(resource,),
        query_window=UtcInterval(
            datetime(2026, 10, 24, 23, tzinfo=UTC),
            datetime(2026, 10, 25, 4, tzinfo=UTC),
        ),
        now=datetime(2026, 1, 1, tzinfo=UTC),
        maximum_horizon=timedelta(days=365),
    )

    result = calculate_availability(request)

    assert [slot.interval.start for slot in result] == [
        datetime(2026, 10, 24, 23, tzinfo=UTC),
        datetime(2026, 10, 25, 0, tzinfo=UTC),
        datetime(2026, 10, 25, 1, tzinfo=UTC),
        datetime(2026, 10, 25, 2, tzinfo=UTC),
    ]


def test_spring_dst_transition_skips_nonexistent_hour() -> None:
    calendars = (
        make_calendar(
            scope, scope.value, start=time(0), end=time(4), weekday=6, timezone_name="Europe/London"
        )
        for scope in (CalendarScope.ORGANIZATION, CalendarScope.LOCATION, CalendarScope.RESOURCE)
    )
    organization, location, resource = calendars
    request = make_request(
        organization=organization,
        location=location,
        resources=(resource,),
        query_window=UtcInterval(
            datetime(2026, 3, 29, 0, tzinfo=UTC), datetime(2026, 3, 29, 5, tzinfo=UTC)
        ),
        now=datetime(2026, 1, 1, tzinfo=UTC),
        maximum_horizon=timedelta(days=365),
    )

    assert [slot.interval.start.hour for slot in calculate_availability(request)] == [0, 1, 2]


def test_different_calendar_timezones_intersect_in_utc() -> None:
    organization = make_calendar(
        CalendarScope.ORGANIZATION,
        "org-a",
        timezone_name="UTC",
    )
    request = make_request(organization=organization)

    assert [slot.interval.start.hour for slot in calculate_availability(request)] == [9, 10, 11, 12]


def test_archived_location_closes_all_resource_availability() -> None:
    location = replace(make_calendar(CalendarScope.LOCATION, "location-a"), archived=True)

    assert calculate_availability(make_request(location=location)) == ()
