"""Real SQL statements exercising tenant filters and optimistic concurrency."""

from dataclasses import replace

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from scheduling.application.errors import (
    CalendarAlreadyExistsError,
    CalendarNotFoundError,
    CalendarVersionConflictError,
)
from scheduling.application.models import TrustedActor
from scheduling.application.policies import CalendarMutationGuard
from scheduling.application.use_cases import ArchiveCalendar, CreateCalendar, GetCalendar
from scheduling.domain.calendar import CalendarScope
from scheduling.infrastructure.persistence.sqlalchemy import (
    CalendarPersistenceMapper,
    SqlAlchemyCalendarRepositoryFactory,
    SqlAlchemyCalendarUnitOfWorkFactory,
)
from tests.support.authorization import GrantAuthorizer
from tests.support.calendar_factory import make_calendar


@pytest.fixture
def factory(
    sqlite_session_factory: async_sessionmaker[AsyncSession],
) -> SqlAlchemyCalendarUnitOfWorkFactory:
    return SqlAlchemyCalendarUnitOfWorkFactory(
        sqlite_session_factory, SqlAlchemyCalendarRepositoryFactory(CalendarPersistenceMapper())
    )


@pytest.mark.asyncio
async def test_commit_persists_and_reads_across_sessions(
    factory: SqlAlchemyCalendarUnitOfWorkFactory,
) -> None:
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")
    async with factory.create() as unit:
        await unit.calendars.add(calendar)
        await unit.commit()

    async with factory.create() as unit:
        assert await unit.calendars.get(calendar.tenant_id, calendar.calendar_id) == calendar
        assert (
            await unit.calendars.get_by_scope(
                calendar.tenant_id, CalendarScope.RESOURCE, "resource-a"
            )
            == calendar
        )
        assert await unit.calendars.list_by_scope(
            calendar.tenant_id, CalendarScope.RESOURCE, "resource-a"
        ) == (calendar,)
        assert (
            await unit.calendars.get_by_scope(calendar.tenant_id, CalendarScope.RESOURCE, "other")
            is None
        )


@pytest.mark.asyncio
async def test_rollback_discards_uncommitted_add(
    factory: SqlAlchemyCalendarUnitOfWorkFactory,
) -> None:
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")
    async with factory.create() as unit:
        await unit.calendars.add(calendar)

    async with factory.create() as unit:
        assert await unit.calendars.get(calendar.tenant_id, calendar.calendar_id) is None


@pytest.mark.asyncio
async def test_duplicate_scope_and_id_are_rejected(
    factory: SqlAlchemyCalendarUnitOfWorkFactory,
) -> None:
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")
    async with factory.create() as unit:
        await unit.calendars.add(calendar)
        await unit.commit()

    for conflicting in (
        calendar,
        replace(calendar, calendar_id="different-id"),
    ):
        with pytest.raises(CalendarAlreadyExistsError):
            async with factory.create() as unit:
                await unit.calendars.add(conflicting)
                await unit.commit()


@pytest.mark.asyncio
async def test_tenant_isolation_with_equal_calendar_identifiers(
    factory: SqlAlchemyCalendarUnitOfWorkFactory,
) -> None:
    first = make_calendar(CalendarScope.RESOURCE, "resource-a")
    second = replace(first, tenant_id="tenant-b")
    async with factory.create() as unit:
        await unit.calendars.add(first)
        await unit.calendars.add(second)
        await unit.commit()

    async with factory.create() as unit:
        assert await unit.calendars.get("tenant-a", first.calendar_id) == first
        assert await unit.calendars.get("tenant-b", first.calendar_id) == second
        assert await unit.calendars.get("tenant-c", first.calendar_id) is None


@pytest.mark.asyncio
async def test_atomic_cas_rejects_stale_update(
    factory: SqlAlchemyCalendarUnitOfWorkFactory,
) -> None:
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")
    async with factory.create() as unit:
        await unit.calendars.add(calendar)
        await unit.commit()

    updated = replace(calendar, version=2, archived=True)
    async with factory.create() as unit:
        await unit.calendars.update_if_version(updated, 1)
        await unit.commit()

    with pytest.raises(CalendarVersionConflictError):
        async with factory.create() as unit:
            await unit.calendars.update_if_version(replace(calendar, version=2), 1)

    async with factory.create() as unit:
        assert await unit.calendars.get(calendar.tenant_id, calendar.calendar_id) == updated


@pytest.mark.asyncio
async def test_wrong_version_or_scope_cannot_modify_calendar(
    factory: SqlAlchemyCalendarUnitOfWorkFactory,
) -> None:
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")
    async with factory.create() as unit:
        await unit.calendars.add(calendar)
        await unit.commit()

    with pytest.raises(CalendarVersionConflictError):
        async with factory.create() as unit:
            await unit.calendars.update_if_version(replace(calendar, version=5), 1)

    with pytest.raises(CalendarVersionConflictError):
        async with factory.create() as unit:
            await unit.calendars.update_if_version(
                replace(calendar, version=2, scope_id="other"), 1
            )

    with pytest.raises(CalendarNotFoundError):
        async with factory.create() as unit:
            await unit.calendars.update_if_version(
                replace(calendar, tenant_id="other", version=2), 1
            )


@pytest.mark.asyncio
async def test_real_application_use_cases_use_sqlalchemy_without_changes(
    factory: SqlAlchemyCalendarUnitOfWorkFactory,
) -> None:
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")
    actor = TrustedActor(tenant_id="tenant-a", actor_id="owner-a")
    authorizer = GrantAuthorizer()
    authorizer.allow_manage(actor, calendar.scope, calendar.scope_id)

    await CreateCalendar(factory, authorizer).execute(actor, calendar)
    assert await GetCalendar(factory, authorizer).execute(actor, calendar.calendar_id) == calendar
    archived = await ArchiveCalendar(factory, CalendarMutationGuard(authorizer)).execute(
        actor, calendar.calendar_id, expected_version=1
    )
    assert archived.archived and archived.version == 2
    assert await GetCalendar(factory, authorizer).execute(actor, calendar.calendar_id) == archived
