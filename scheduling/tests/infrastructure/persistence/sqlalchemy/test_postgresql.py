"""PostgreSQL-only integration gates; CI provisions an actual PostgreSQL server."""

import asyncio
import os
from collections.abc import AsyncIterator
from dataclasses import replace

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Column, Integer, MetaData, Table
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from scheduling.application.errors import CalendarAlreadyExistsError, CalendarVersionConflictError
from scheduling.domain.calendar import CalendarScope
from scheduling.infrastructure.persistence.sqlalchemy import (
    CalendarPersistenceMapper,
    SqlAlchemyCalendarRepositoryFactory,
    SqlAlchemyCalendarUnitOfWorkFactory,
    scheduling_metadata,
)
from tests.support.calendar_factory import make_calendar


@pytest.fixture
async def postgres_engine() -> AsyncIterator[AsyncEngine]:
    url = os.getenv("SCHEDULING_TEST_POSTGRES_URL")
    if not url:
        pytest.skip("Real PostgreSQL is required; set SCHEDULING_TEST_POSTGRES_URL.")
    engine = create_async_engine(url, pool_size=5)
    async with engine.begin() as connection:
        await connection.run_sync(scheduling_metadata().drop_all)
        await connection.run_sync(scheduling_metadata().create_all)
    try:
        yield engine
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(scheduling_metadata().drop_all)
        await engine.dispose()


@pytest.fixture
def postgres_factory(postgres_engine: AsyncEngine) -> SqlAlchemyCalendarUnitOfWorkFactory:
    return SqlAlchemyCalendarUnitOfWorkFactory(
        async_sessionmaker(postgres_engine, expire_on_commit=False),
        SqlAlchemyCalendarRepositoryFactory(CalendarPersistenceMapper()),
    )


@pytest.mark.asyncio
async def test_parallel_edits_cannot_both_commit(
    postgres_factory: SqlAlchemyCalendarUnitOfWorkFactory,
) -> None:
    original = make_calendar(CalendarScope.RESOURCE, "resource-a")
    async with postgres_factory.create() as unit:
        await unit.calendars.add(original)
        await unit.commit()

    ready = asyncio.Barrier(2)

    async def modify(archived: bool) -> str:
        async with postgres_factory.create() as unit:
            snapshot = await unit.calendars.get(original.tenant_id, original.calendar_id)
            assert snapshot is not None
            assert snapshot == original
            await ready.wait()
            try:
                await unit.calendars.update_if_version(
                    replace(snapshot, version=2, archived=archived), 1
                )
                await unit.commit()
            except CalendarVersionConflictError:
                return "conflict"
            return "committed"

    results = await asyncio.wait_for(asyncio.gather(modify(True), modify(False)), timeout=15)
    assert sorted(results) == ["committed", "conflict"]

    async with postgres_factory.create() as unit:
        persisted = await unit.calendars.get(original.tenant_id, original.calendar_id)
        assert persisted is not None and persisted.version == 2


@pytest.mark.asyncio
async def test_postgres_duplicate_scope_is_translated_and_rolled_back(
    postgres_factory: SqlAlchemyCalendarUnitOfWorkFactory,
) -> None:
    calendar = make_calendar(CalendarScope.RESOURCE, "resource-a")
    async with postgres_factory.create() as unit:
        await unit.calendars.add(calendar)
        await unit.commit()

    with pytest.raises(CalendarAlreadyExistsError):
        async with postgres_factory.create() as unit:
            await unit.calendars.add(replace(calendar, calendar_id="another-id"))
            await unit.commit()

    async with postgres_factory.create() as unit:
        assert await unit.calendars.list_by_scope(
            calendar.tenant_id, calendar.scope, calendar.scope_id
        ) == (calendar,)


@pytest.mark.asyncio
async def test_postgres_jsonb_and_host_metadata_autogeneration(
    postgres_engine: AsyncEngine,
) -> None:
    host = MetaData()
    Table("host_test_accounts", host, Column("id", Integer, primary_key=True))
    async with postgres_engine.begin() as connection:
        await connection.run_sync(host.create_all)

        def check_migrations(sync_connection: object) -> None:
            from sqlalchemy.engine import Connection

            assert isinstance(sync_connection, Connection)
            context = MigrationContext.configure(sync_connection)
            combined = MetaData()
            for source in (host, scheduling_metadata()):
                for table in source.tables.values():
                    table.to_metadata(combined)
            assert compare_metadata(context, combined) == []

        await connection.run_sync(check_migrations)

    calendar_table = scheduling_metadata().tables["scheduling_calendars"]
    assert calendar_table.c.weekly_schedule.type.compile(dialect=postgres_engine.dialect) == "JSONB"
