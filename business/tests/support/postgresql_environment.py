import os
from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from business.infrastructure.persistence.sqlalchemy import (
    BranchMapper,
    BusinessBase,
    BusinessMapper,
    MembershipAuditMapper,
    MembershipMapper,
    SqlAlchemyBusinessUnitOfWorkFactory,
)
from tests.support.sqlalchemy_environment import SqlAlchemyEnvironment


@pytest.fixture
async def postgresql_environment() -> AsyncGenerator[SqlAlchemyEnvironment]:
    dsn = os.environ.get("BUSINESS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("PostgreSQL integration requires BUSINESS_TEST_POSTGRES_DSN")
    schema = f"business_test_{uuid4().hex}"
    admin_engine = create_async_engine(dsn)
    async with admin_engine.begin() as connection:
        await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = admin_engine.execution_options(schema_translate_map={None: schema})
    try:
        async with engine.begin() as connection:
            await connection.run_sync(BusinessBase.metadata.create_all)
        factory = SqlAlchemyBusinessUnitOfWorkFactory(
            async_sessionmaker(engine, expire_on_commit=False),
            BusinessMapper(),
            BranchMapper(),
            MembershipMapper(),
            MembershipAuditMapper(),
        )
        yield SqlAlchemyEnvironment(engine, factory)
    finally:
        await engine.dispose()
        async with admin_engine.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin_engine.dispose()
