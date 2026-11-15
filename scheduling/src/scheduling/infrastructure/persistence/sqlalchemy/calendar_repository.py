"""Atomic, tenant-scoped asynchronous calendar repository."""

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from scheduling.application.errors import CalendarNotFoundError, CalendarVersionConflictError
from scheduling.domain.calendar import Calendar, CalendarScope

from .calendar_mapper import CalendarPersistenceMapper
from .calendar_record import CalendarRecord


class SqlAlchemyCalendarRepository:
    """All queries bind tenant identity; writes use database-level CAS."""

    def __init__(self, session: AsyncSession, mapper: CalendarPersistenceMapper) -> None:
        self._session = session
        self._mapper = mapper

    async def get(self, tenant_id: str, calendar_id: str) -> Calendar | None:
        record = await self._session.get(CalendarRecord, (tenant_id, calendar_id))
        return None if record is None else self._mapper.to_domain(record)

    async def get_by_scope(
        self, tenant_id: str, scope: CalendarScope, scope_id: str
    ) -> Calendar | None:
        statement = select(CalendarRecord).where(
            CalendarRecord.tenant_id == tenant_id,
            CalendarRecord.scope == scope.value,
            CalendarRecord.scope_id == scope_id,
        )
        record = (await self._session.scalars(statement)).one_or_none()
        return None if record is None else self._mapper.to_domain(record)

    async def list_by_scope(
        self, tenant_id: str, scope: CalendarScope, scope_id: str
    ) -> tuple[Calendar, ...]:
        statement = (
            select(CalendarRecord)
            .where(
                CalendarRecord.tenant_id == tenant_id,
                CalendarRecord.scope == scope.value,
                CalendarRecord.scope_id == scope_id,
            )
            .order_by(CalendarRecord.calendar_id)
        )
        records = (await self._session.scalars(statement)).all()
        return tuple(self._mapper.to_domain(record) for record in records)

    async def add(self, calendar: Calendar) -> None:
        self._session.add(self._mapper.to_record(calendar))

    async def update_if_version(self, calendar: Calendar, expected_version: int) -> None:
        if calendar.version != expected_version + 1:
            raise CalendarVersionConflictError("Calendar version must advance by one.")
        values = self._mapper.to_values(calendar)
        for identity_field in ("calendar_id", "tenant_id", "scope", "scope_id"):
            values.pop(identity_field)
        statement = (
            update(CalendarRecord)
            .where(
                CalendarRecord.tenant_id == calendar.tenant_id,
                CalendarRecord.calendar_id == calendar.calendar_id,
                CalendarRecord.scope == calendar.scope.value,
                CalendarRecord.scope_id == calendar.scope_id,
                CalendarRecord.version == expected_version,
            )
            .values(**values)
            .execution_options(synchronize_session=False)
        )
        result = await self._session.execute(statement)
        if result.rowcount != 1:  # type: ignore[attr-defined]
            existing = await self.get(calendar.tenant_id, calendar.calendar_id)
            if existing is None:
                raise CalendarNotFoundError("Calendar not found in tenant.")
            raise CalendarVersionConflictError("Calendar was updated by another transaction.")
