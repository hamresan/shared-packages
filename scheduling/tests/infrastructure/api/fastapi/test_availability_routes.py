"""Host-authorized availability reads from independent resource schedules."""

from datetime import UTC, datetime

import pytest
from httpx import AsyncClient

from scheduling.domain.calendar import CalendarScope
from scheduling.domain.time import UtcInterval
from scheduling.engine import BusyInterval
from tests.support.api.host_factory import HttpTestHost
from tests.support.api.payloads import availability_payload, calendar_payload


@pytest.mark.asyncio
async def test_two_resource_schedules_with_external_busy_periods(
    client: AsyncClient, http_host: HttpTestHost
) -> None:
    actor = http_host.actor_provider.actor
    inputs = (
        (CalendarScope.ORGANIZATION, "org-1", 8, 18),
        (CalendarScope.LOCATION, "location-1", 8, 18),
        (CalendarScope.RESOURCE, "resource-1", 9, 11),
        (CalendarScope.RESOURCE, "resource-2", 13, 15),
    )
    for scope, scope_id, start, end in inputs:
        http_host.authorizer.allow_manage(actor, scope, scope_id)
        response = await client.post(
            "/scheduling/calendars",
            json=calendar_payload(scope.value, scope_id, start_hour=start, end_hour=end),
        )
        assert response.status_code == 201, response.text

    http_host.busy_reader.intervals = (
        BusyInterval(
            "resource-2",
            UtcInterval(
                datetime(2026, 11, 16, 9, tzinfo=UTC), datetime(2026, 11, 16, 10, tzinfo=UTC)
            ),
        ),
    )
    response = await client.post(
        "/scheduling/availability", json=availability_payload(["resource-1", "resource-2"])
    )
    assert response.status_code == 200, response.text
    assert [item["resource_id"] for item in response.json()] == [
        "resource-1",
        "resource-1",
        "resource-2",
    ]
    assert http_host.busy_reader.calls[0][0] == "tenant-a"


@pytest.mark.asyncio
async def test_ungranted_resource_is_rejected_before_busy_reader_is_called(
    client: AsyncClient, http_host: HttpTestHost
) -> None:
    actor = http_host.actor_provider.actor
    http_host.authorizer.allow_read(actor, CalendarScope.ORGANIZATION, "org-1")
    http_host.authorizer.allow_read(actor, CalendarScope.LOCATION, "location-1")
    response = await client.post(
        "/scheduling/availability", json=availability_payload(["resource-other"])
    )
    assert response.status_code == 403
    assert not http_host.busy_reader.calls


@pytest.mark.asyncio
async def test_missing_authorized_calendar_does_not_return_bookable_slots(
    client: AsyncClient, http_host: HttpTestHost
) -> None:
    actor = http_host.actor_provider.actor
    for scope, identifier in (
        (CalendarScope.ORGANIZATION, "org-1"),
        (CalendarScope.LOCATION, "location-1"),
        (CalendarScope.RESOURCE, "resource-1"),
    ):
        http_host.authorizer.allow_read(actor, scope, identifier)

    response = await client.post(
        "/scheduling/availability", json=availability_payload(["resource-1"])
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_invalid_utc_window_is_not_silently_normalized(
    client: AsyncClient, http_host: HttpTestHost
) -> None:
    payload = availability_payload(["resource-1"])
    payload["start"] = "2026-11-16T09:00:00"
    response = await client.post("/scheduling/availability", json=payload)
    assert response.status_code == 422
