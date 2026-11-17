"""Host-owned Alembic revision smoke tests on isolated PostgreSQL schemas."""

import os
from uuid import uuid4

import pytest
from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from sqlalchemy import Connection, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from customer.migrations import customer_metadata, install_customer_rls


def apply_customer_in_host_revision(connection: Connection) -> None:
    """Exercise Customer DDL/policy composition inside an Alembic revision context."""
    migration = MigrationContext.configure(connection)
    operations = Operations(migration)
    customer_metadata().create_all(operations.get_bind(), checkfirst=True)
    install_customer_rls(operations.get_bind())


@pytest.mark.parametrize("existing_host_table", [False, True])
async def test_alembic_composition_preserves_unrelated_schema(
    postgres_sessions: async_sessionmaker[AsyncSession],
    existing_host_table: bool,
) -> None:
    _ = postgres_sessions  # Fixture ensures PostgreSQL acceptance is explicitly configured.
    dsn = os.environ["CUSTOMER_TEST_POSTGRES_DSN"]
    engine = create_async_engine(dsn)
    schema = f"customer_accept_{uuid4().hex}"
    try:
        async with engine.begin() as connection:
            # Schema is an exclusive, randomly generated test target, never user input.
            await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
            await connection.execute(text(f'SET LOCAL search_path TO "{schema}"'))
            if existing_host_table:
                await connection.execute(text("CREATE TABLE host_owned (id integer PRIMARY KEY)"))
                await connection.execute(text("INSERT INTO host_owned VALUES (42)"))
            await connection.run_sync(apply_customer_in_host_revision)
            await connection.run_sync(apply_customer_in_host_revision)

            count = await connection.scalar(
                text(
                    "SELECT count(*) FROM information_schema.tables "
                    "WHERE table_schema=:schema AND table_name LIKE 'customer_%'"
                ),
                {"schema": schema},
            )
            assert count == len(customer_metadata().tables)
            if existing_host_table:
                assert await connection.scalar(text("SELECT id FROM host_owned")) == 42
    finally:
        async with engine.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        await engine.dispose()
