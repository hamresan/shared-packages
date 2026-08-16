from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from identity.infrastructure.persistence.sqlalchemy.base import IdentityBase
from identity.infrastructure.persistence.sqlalchemy.unit_of_work import SqlAlchemyIdentityUnitOfWork


@pytest.mark.asyncio
async def test_unit_of_work_uses_host_session_factory() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as connection:
        await connection.run_sync(IdentityBase.metadata.create_all)

    @asynccontextmanager
    async def session_factory() -> AsyncGenerator[AsyncSession]:
        async with session_maker() as session:
            yield session

    unit_of_work = SqlAlchemyIdentityUnitOfWork(session_factory)

    async with unit_of_work.transaction() as session:
        assert isinstance(session, AsyncSession)

    await engine.dispose()
