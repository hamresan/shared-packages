"""Shared atomic state enforcing calendar uniqueness and version conflicts."""

import asyncio

from scheduling.application.errors import (
    CalendarAlreadyExistsError,
    CalendarNotFoundError,
    CalendarVersionConflictError,
)
from scheduling.domain.calendar import Calendar


class InMemoryCalendarStore:
    def __init__(self) -> None:
        self.records: dict[tuple[str, str], Calendar] = {}
        self._lock = asyncio.Lock()

    def seed(self, calendar: Calendar) -> None:
        self.records[(calendar.tenant_id, calendar.calendar_id)] = calendar

    async def commit(
        self, creates: tuple[Calendar, ...], updates: tuple[tuple[Calendar, int], ...]
    ) -> None:
        async with self._lock:
            candidate = dict(self.records)
            for calendar in creates:
                key = (calendar.tenant_id, calendar.calendar_id)
                scope_exists = any(
                    existing.tenant_id == calendar.tenant_id
                    and existing.scope == calendar.scope
                    and existing.scope_id == calendar.scope_id
                    for existing in candidate.values()
                )
                if key in candidate or scope_exists:
                    raise CalendarAlreadyExistsError("Calendar ID or tenant scope already exists.")
                candidate[key] = calendar

            for calendar, expected_version in updates:
                key = (calendar.tenant_id, calendar.calendar_id)
                previous = candidate.get(key)
                if previous is None:
                    raise CalendarNotFoundError("Calendar was removed before commit.")
                if previous.version != expected_version:
                    raise CalendarVersionConflictError("Concurrent calendar update detected.")
                if calendar.version != expected_version + 1:
                    raise CalendarVersionConflictError("Calendar revision must advance by one.")
                if (previous.tenant_id, previous.scope, previous.scope_id) != (
                    calendar.tenant_id,
                    calendar.scope,
                    calendar.scope_id,
                ):
                    raise ValueError("A calendar's trusted tenant and scope cannot be reassigned.")
                candidate[key] = calendar

            self.records = candidate
