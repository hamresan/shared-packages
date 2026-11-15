"""Different host domains use the same scheduling API without shared host entities."""

from datetime import UTC, datetime, time, timedelta

from scheduling.domain.calendar import CalendarScope
from scheduling.domain.time import UtcInterval
from scheduling.engine import BusyInterval, calculate_availability
from tests.support.calendar_factory import make_calendar, make_request


def test_clinic_host_supplies_occupied_staff_and_independent_shifts() -> None:
    first = make_calendar(CalendarScope.RESOURCE, "clinician-a", end=time(11))
    second = make_calendar(CalendarScope.RESOURCE, "clinician-b", start=time(13), end=time(15))
    request = make_request(
        resources=(first, second),
        busy_intervals=(
            BusyInterval(
                "clinician-a",
                UtcInterval(
                    datetime(2026, 11, 16, 5, tzinfo=UTC),
                    datetime(2026, 11, 16, 6, tzinfo=UTC),
                ),
            ),
        ),
    )

    slots = calculate_availability(request)

    assert [(slot.resource_id, slot.interval.start.hour) for slot in slots] == [
        ("clinician-a", 6),
        ("clinician-b", 9),
        ("clinician-b", 10),
    ]


def test_room_host_uses_european_timezone_and_buffers_without_booking_entities() -> None:
    organization = make_calendar(
        CalendarScope.ORGANIZATION, "facility", timezone_name="Europe/London"
    )
    location = make_calendar(CalendarScope.LOCATION, "office", timezone_name="Europe/London")
    room = make_calendar(
        CalendarScope.RESOURCE,
        "meeting-room-1",
        start=time(10),
        end=time(12),
        timezone_name="Europe/London",
    )
    request = make_request(
        organization=organization,
        location=location,
        resources=(room,),
        duration=timedelta(minutes=30),
        step=timedelta(minutes=30),
        buffer_before=timedelta(minutes=15),
        buffer_after=timedelta(minutes=15),
    )

    slots = calculate_availability(request)

    assert [slot.interval.start.strftime("%H:%M") for slot in slots] == [
        "10:15",
        "10:45",
        "11:15",
    ]
