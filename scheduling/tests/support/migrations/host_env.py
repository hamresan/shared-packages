"""Alembic environment owned by a sample host, not by the scheduling distribution."""

import asyncio

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from scheduling.infrastructure.persistence.sqlalchemy import render_scheduling_type
from tests.support.migrations.host_metadata import combined_metadata

configuration = context.config
target_metadata = combined_metadata()


def run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        render_item=render_scheduling_type,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    section = configuration.get_section(configuration.config_ini_section, {})
    connectable = async_engine_from_config(section, prefix="sqlalchemy.", poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(run_migrations)
    await connectable.dispose()


def run_offline_migrations() -> None:
    context.configure(
        url=configuration.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_offline_migrations()
else:
    asyncio.run(run_async_migrations())
