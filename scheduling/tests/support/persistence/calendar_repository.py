"""Repository fake that stages writes for atomic Unit of Work commit."""

from scheduling.domain.calendar import Calendar, CalendarScope

from .calendar_store import InMemoryCalendarStore


class InMemoryCalendarRepository:
    def __init__(self, store: InMemoryCalendarStore) -> None:
        self._store = store
        self.creates: list[Calendar] = []
        self.updates: list[tuple[Calendar, int]] = []

    async def get(self, tenant_id: str, calendar_id: str) -> Calendar | None:
        return self._store.records.get((tenant_id, calendar_id))

    async def get_by_scope(
        self, tenant_id: str, scope: CalendarScope, scope_id: str
    ) -> Calendar | None:
        calendars = await self.list_by_scope(tenant_id, scope, scope_id)
        return calendars[0] if calendars else None

    async def list_by_scope(
        self, tenant_id: str, scope: CalendarScope, scope_id: str
    ) -> tuple[Calendar, ...]:
        return tuple(
            calendar
            for calendar in self._store.records.values()
            if calendar.tenant_id == tenant_id
            and calendar.scope == scope
            and calendar.scope_id == scope_id
        )

    async def add(self, calendar: Calendar) -> None:
        self.creates.append(calendar)

    async def update_if_version(self, calendar: Calendar, expected_version: int) -> None:
        self.updates.append((calendar, expected_version))
