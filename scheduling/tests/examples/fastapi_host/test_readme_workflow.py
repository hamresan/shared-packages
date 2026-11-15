"""Exercise the documented calendar-to-availability HTTP workflow end to end."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from examples.fastapi_host.app import create_app
from tests.support.api.payloads import calendar_payload


@pytest.mark.asyncio
async def test_readme_host_workflow_returns_slots_and_enforces_versions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SCHEDULING_DEMO_API_KEY", "readme-demo-key")
    monkeypatch.setenv("SCHEDULING_DEMO_DB_URL", f"sqlite+aiosqlite:///{tmp_path / 'readme.db'}")
    app = create_app()
    headers = {"X-API-Key": "readme-demo-key"}
    today = datetime.now(UTC).date()
    next_monday = today + timedelta(days=(7 - today.weekday()) % 7 or 7)

    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            for scope, scope_id in (
                ("organization", "org-1"),
                ("location", "location-1"),
                ("resource", "resource-1"),
            ):
                created = await client.post(
                    "/scheduling/calendars",
                    headers=headers,
                    json=calendar_payload(scope, scope_id),
                )
                assert created.status_code == 201, created.text

            query = {
                "organization_id": "org-1",
                "location_id": "location-1",
                "resource_ids": ["resource-1"],
                "start": f"{next_monday.isoformat()}T00:00:00Z",
                "end": f"{next_monday.isoformat()}T23:59:59Z",
                "duration_minutes": 30,
                "step_minutes": 30,
            }
            available = await client.post("/scheduling/availability", headers=headers, json=query)
            assert available.status_code == 200, available.text
            slots = available.json()
            assert len(slots) == 16
            assert all(slot["resource_id"] == "resource-1" for slot in slots)
            assert slots[0]["start"].endswith("T05:00:00Z")

            update = {
                "expected_version": 1,
                "weekly_schedule": {
                    "days": [
                        {"weekday": 0, "windows": [{"start": "10:00", "end": "16:00"}]}
                    ]
                },
            }
            route = "/scheduling/calendars/calendar-resource-1/weekly-schedule"
            changed = await client.put(route, headers=headers, json=update)
            assert changed.status_code == 200, changed.text
            assert changed.json()["version"] == 2

            stale = await client.put(route, headers=headers, json=update)
            assert stale.status_code == 409
