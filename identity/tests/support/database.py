from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from identity.infrastructure.persistence.sqlalchemy import IdentityBase


class SqliteIdentityDatabase:
    def __init__(self) -> None:
        self._engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        self._session_maker = async_sessionmaker(self._engine, expire_on_commit=False)

    async def start(self) -> None:
        async with self._engine.begin() as connection:
            await connection.run_sync(IdentityBase.metadata.create_all)

    async def close(self) -> None:
        await self._engine.dispose()

    @asynccontextmanager
    async def session_factory(self) -> AsyncGenerator[AsyncSession]:
        async with self._session_maker() as session:
            yield session
