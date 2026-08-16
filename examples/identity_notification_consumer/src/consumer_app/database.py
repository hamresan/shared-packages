from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from identity.infrastructure.persistence.sqlalchemy import IdentityBase
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool


class ConsumerDatabase:
    def __init__(self) -> None:
        self.engine: AsyncEngine = create_async_engine(
            "sqlite+aiosqlite://",
            poolclass=StaticPool,
        )
        self._session_maker = async_sessionmaker(self.engine, expire_on_commit=False)

    @asynccontextmanager
    async def session_factory(self) -> AsyncGenerator[AsyncSession]:
        async with self._session_maker() as session:
            yield session

    async def create_schema(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(IdentityBase.metadata.create_all)

    async def close(self) -> None:
        await self.engine.dispose()
