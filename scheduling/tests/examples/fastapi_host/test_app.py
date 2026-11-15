"""Run the shipped example host with a real file-backed SQLAlchemy adapter."""

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from examples.fastapi_host.app import create_app
from tests.support.api.payloads import calendar_payload


@pytest.mark.asyncio
async def test_host_api_key_two_locations_and_resource_ownership(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SCHEDULING_DEMO_API_KEY", "test-secret")
    monkeypatch.setenv("SCHEDULING_DEMO_DB_URL", f"sqlite+aiosqlite:///{tmp_path / 'host.db'}")
    app = create_app()
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            unauthorized = await client.get("/scheduling/calendars/calendar-org-1")
            assert unauthorized.status_code == 401

            for scope, scope_id in (
                ("organization", "org-1"),
                ("location", "location-1"),
                ("location", "location-2"),
                ("resource", "resource-1"),
                ("resource", "resource-2"),
            ):
                created = await client.post(
                    "/scheduling/calendars",
                    headers={"X-API-Key": "test-secret"},
                    json=calendar_payload(scope, scope_id),
                )
                assert created.status_code == 201, created.text

            first_location = await client.get(
                "/scheduling/calendars/calendar-location-1",
                headers={"X-API-Key": "test-secret"},
            )
            second_location = await client.get(
                "/scheduling/calendars/calendar-location-2",
                headers={"X-API-Key": "test-secret"},
            )
            assert first_location.status_code == second_location.status_code == 200

            denied = await client.post(
                "/scheduling/calendars",
                headers={"X-API-Key": "test-secret"},
                json=calendar_payload("resource", "outside-allowed-scopes"),
            )
            assert denied.status_code == 403
