"""Real HTTP flow tests: authentication, authorization, validation and versioning."""

import pytest
from httpx import AsyncClient

from scheduling.domain.calendar import CalendarScope
from tests.support.api.host_factory import HttpTestHost
from tests.support.api.payloads import calendar_payload


@pytest.mark.asyncio
async def test_calendar_management_crud_and_version_conflicts(
    client: AsyncClient, http_host: HttpTestHost
) -> None:
    actor = http_host.actor_provider.actor
    http_host.authorizer.allow_manage(actor, CalendarScope.RESOURCE, "resource-1")
    payload = calendar_payload("resource", "resource-1")

    created = await client.post("/scheduling/calendars", json=payload)
    assert created.status_code == 201, created.text
    assert created.json()["tenant_id"] == "tenant-a"
    assert created.json()["version"] == 1

    fetched = await client.get("/scheduling/calendars/calendar-resource-1")
    assert fetched.status_code == 200
    listed = await client.get(
        "/scheduling/calendars", params={"scope": "resource", "scope_id": "resource-1"}
    )
    assert [item["calendar_id"] for item in listed.json()] == ["calendar-resource-1"]

    schedule = {
        "expected_version": 1,
        "weekly_schedule": {
            "days": [{"weekday": 0, "windows": [{"start": "10:00", "end": "15:00"}]}]
        },
    }
    changed = await client.put(
        "/scheduling/calendars/calendar-resource-1/weekly-schedule", json=schedule
    )
    assert changed.status_code == 200, changed.text
    assert changed.json()["version"] == 2
    assert changed.json()["weekly_schedule"]["days"][0]["windows"][0]["start"] == "10:00:00"

    stale = await client.put(
        "/scheduling/calendars/calendar-resource-1/weekly-schedule", json=schedule
    )
    assert stale.status_code == 409

    duplicate = await client.post("/scheduling/calendars", json=payload)
    assert duplicate.status_code == 409

    archived = await client.post(
        "/scheduling/calendars/calendar-resource-1/archive", json={"expected_version": 2}
    )
    assert archived.status_code == 200 and archived.json()["archived"]
    assert archived.json()["version"] == 3


@pytest.mark.asyncio
async def test_calendar_date_exceptions_and_blocked_periods(
    client: AsyncClient, http_host: HttpTestHost
) -> None:
    http_host.authorizer.allow_manage(
        http_host.actor_provider.actor, CalendarScope.RESOURCE, "resource-1"
    )
    await client.post("/scheduling/calendars", json=calendar_payload("resource", "resource-1"))
    name = "/scheduling/calendars/calendar-resource-1"

    closed = await client.put(
        f"{name}/exceptions",
        json={"expected_version": 1, "exception": {"day": "2026-11-16", "closed": True}},
    )
    assert closed.status_code == 200 and closed.json()["exceptions"][0]["closed"]
    removed = await client.delete(f"{name}/exceptions/2026-11-16", params={"expected_version": 2})
    assert removed.status_code == 200 and removed.json()["exceptions"] == []

    block = {"start": "2026-11-16T06:00:00Z", "end": "2026-11-16T07:00:00Z"}
    blocked = await client.post(
        f"{name}/blocked-periods", json={"expected_version": 3, "block": block}
    )
    assert blocked.status_code == 200 and len(blocked.json()["blocked_periods"]) == 1
    unblocked = await client.request(
        "DELETE", f"{name}/blocked-periods", json={"expected_version": 4, "block": block}
    )
    assert unblocked.status_code == 200 and unblocked.json()["blocked_periods"] == []


@pytest.mark.asyncio
async def test_denied_unauthenticated_and_untrusted_scope(
    client: AsyncClient, http_host: HttpTestHost
) -> None:
    payload = calendar_payload("resource", "resource-1")
    payload["tenant_id"] = "tenant-b"

    untrusted_tenant = await client.post("/scheduling/calendars", json=payload)
    assert untrusted_tenant.status_code == 422

    payload.pop("tenant_id")
    denied = await client.post("/scheduling/calendars", json=payload)
    assert denied.status_code == 403

    http_host.actor_provider.authenticated = False
    unauthorized = await client.post("/scheduling/calendars", json=payload)
    assert unauthorized.status_code == 401
    http_host.actor_provider.authenticated = True

    http_host.authorizer.allow_manage(
        http_host.actor_provider.actor, CalendarScope.RESOURCE, "resource-1"
    )
    accepted = await client.post("/scheduling/calendars", json=payload)
    assert accepted.status_code == 201
    assert accepted.json()["tenant_id"] == "tenant-a"

    missing = await client.get("/scheduling/calendars/does-not-exist")
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_invalid_schedule_is_rejected_without_persistence(
    client: AsyncClient, http_host: HttpTestHost
) -> None:
    http_host.authorizer.allow_manage(
        http_host.actor_provider.actor, CalendarScope.RESOURCE, "resource-1"
    )
    payload = calendar_payload("resource", "resource-1")
    payload["weekly_schedule"]["days"][0]["windows"][0]["end"] = "09:00:00"
    invalid = await client.post("/scheduling/calendars", json=payload)
    assert invalid.status_code == 422
    missing = await client.get("/scheduling/calendars/calendar-resource-1")
    assert missing.status_code == 404
