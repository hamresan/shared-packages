"""Ephemeral PostgreSQL schema and an explicitly non-bypass runtime role."""

import os
from collections.abc import AsyncIterator
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from customer.migrations import customer_metadata, install_customer_rls


@pytest.fixture
async def postgres_sessions() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    dsn = os.environ.get("CUSTOMER_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("PostgreSQL acceptance requires CUSTOMER_TEST_POSTGRES_DSN")

    admin = create_async_engine(dsn)
    runtime_role = f"customer_test_{uuid4().hex[:16]}"
    runtime_password = uuid4().hex
    async with admin.begin() as connection:
        # Identifiers and password are generated from hex UUIDs, never external input.
        await connection.execute(
            text(f"CREATE ROLE \"{runtime_role}\" LOGIN PASSWORD '{runtime_password}'")
        )
        await connection.run_sync(customer_metadata().create_all)
        await connection.run_sync(install_customer_rls)
        await connection.execute(text(f'GRANT USAGE ON SCHEMA public TO "{runtime_role}"'))
        for table_name in customer_metadata().tables:
            await connection.execute(
                text(f'GRANT SELECT, INSERT, UPDATE, DELETE ON "{table_name}" TO "{runtime_role}"')
            )

    runtime_url = make_url(dsn).set(username=runtime_role, password=runtime_password)
    runtime = create_async_engine(runtime_url)
    try:
        yield async_sessionmaker(runtime, expire_on_commit=False)
    finally:
        await runtime.dispose()
        async with admin.begin() as connection:
            await connection.run_sync(customer_metadata().drop_all)
            await connection.execute(text(f'DROP ROLE "{runtime_role}"'))
        await admin.dispose()
