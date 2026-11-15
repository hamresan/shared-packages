"""Tenant-scoped calendar persistence contract with atomic compare-and-swap."""

from typing import Protocol

from scheduling.domain.calendar import Calendar, CalendarScope


class CalendarRepository(Protocol):
    async def get(self, tenant_id: str, calendar_id: str) -> Calendar | None: ...

    async def get_by_scope(
        self, tenant_id: str, scope: CalendarScope, scope_id: str
    ) -> Calendar | None: ...

    async def list_by_scope(
        self, tenant_id: str, scope: CalendarScope, scope_id: str
    ) -> tuple[Calendar, ...]: ...

    async def add(self, calendar: Calendar) -> None:
        """Stage creation; a transaction must enforce unique calendar/scope identifiers."""
        ...

    async def update_if_version(self, calendar: Calendar, expected_version: int) -> None:
        """Stage a CAS update; commit must atomically reject stale versions."""
        ...
