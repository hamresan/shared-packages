"""Reusable HTTP request payload builders for calendar and availability scenarios."""

from typing import Any


def calendar_payload(
    scope: str, scope_id: str, *, start_hour: int = 9, end_hour: int = 17
) -> dict[str, Any]:
    return {
        "calendar_id": f"calendar-{scope_id}",
        "scope": scope,
        "scope_id": scope_id,
        "timezone": "Asia/Muscat",
        "weekly_schedule": {
            "days": [
                {
                    "weekday": 0,
                    "windows": [
                        {"start": f"{start_hour:02d}:00:00", "end": f"{end_hour:02d}:00:00"}
                    ],
                }
            ]
        },
    }


def availability_payload(resource_ids: list[str]) -> dict[str, Any]:
    return {
        "organization_id": "org-1",
        "location_id": "location-1",
        "resource_ids": resource_ids,
        "start": "2026-11-16T00:00:00Z",
        "end": "2026-11-17T00:00:00Z",
        "duration_minutes": 60,
        "step_minutes": 60,
    }
