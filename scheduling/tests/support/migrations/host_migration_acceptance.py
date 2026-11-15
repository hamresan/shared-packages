"""Assert a real host revision upgrades, stores data, and reverses cleanly."""

import asyncio
from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from scheduling.domain.calendar import CalendarScope
from scheduling.infrastructure.persistence.sqlalchemy import (
    CalendarPersistenceMapper,
    SqlAlchemyCalendarRepositoryFactory,
    SqlAlchemyCalendarUnitOfWorkFactory,
)
from tests.support.calendar_factory import make_calendar

from .host_alembic_runner import HostAlembicRunner
from .host_metadata import combined_metadata


async def assert_host_revision_lifecycle(database_url: str, work_directory: Path) -> None:
    """Use only a disposable database; the migration test intentionally drops its tables."""
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(combined_metadata().drop_all)
            await connection.execute(text("DROP TABLE IF EXISTS alembic_version"))

        runner = HostAlembicRunner(work_directory, database_url)
        revision_path = await asyncio.to_thread(runner.create_and_upgrade)
        revision_text = revision_path.read_text(encoding="utf-8")
        assert "host_migration_accounts" in revision_text
        assert "scheduling_calendars" in revision_text

        def verify_schema(connection: Connection) -> None:
            tables = set(inspect(connection).get_table_names())
            assert {"host_migration_accounts", "scheduling_calendars"} <= tables
            context = MigrationContext.configure(connection)
            assert compare_metadata(context, combined_metadata()) == []

        async with engine.connect() as connection:
            await connection.run_sync(verify_schema)

        sessions = async_sessionmaker(engine, expire_on_commit=False)
        factory = SqlAlchemyCalendarUnitOfWorkFactory(
            sessions, SqlAlchemyCalendarRepositoryFactory(CalendarPersistenceMapper())
        )
        calendar = make_calendar(CalendarScope.RESOURCE, "migrated-resource")
        async with factory.create() as unit:
            await unit.calendars.add(calendar)
            await unit.commit()
        async with factory.create() as unit:
            assert await unit.calendars.get(calendar.tenant_id, calendar.calendar_id) == calendar

        async with engine.begin() as connection:
            await connection.execute(
                text("INSERT INTO host_migration_accounts (id, name) VALUES (1, 'Host account')")
            )
            account = await connection.scalar(
                text("SELECT name FROM host_migration_accounts WHERE id = 1")
            )
            assert account == "Host account"

        await asyncio.to_thread(runner.downgrade)

        def verify_downgrade(connection: Connection) -> None:
            tables = set(inspect(connection).get_table_names())
            assert "host_migration_accounts" not in tables
            assert "scheduling_calendars" not in tables

        async with engine.connect() as connection:
            await connection.run_sync(verify_downgrade)
    finally:
        await engine.dispose()
