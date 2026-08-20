from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from identity.infrastructure.persistence.sqlalchemy import IdentityBase
from tests.support.database_contracts import IdentityTestDatabase


class PostgresqlIdentityDatabase(IdentityTestDatabase):
    def __init__(self, dsn: str) -> None:
        self._engine = create_async_engine(dsn)
        self._session_maker = async_sessionmaker(self._engine, expire_on_commit=False)

    async def start(self) -> None:
        async with self._engine.begin() as connection:
            await connection.run_sync(IdentityBase.metadata.drop_all)
            await connection.run_sync(IdentityBase.metadata.create_all)

    async def close(self) -> None:
        await self._engine.dispose()

    @asynccontextmanager
    async def session_factory(self) -> AsyncGenerator[AsyncSession]:
        async with self._session_maker() as session:
            yield session
