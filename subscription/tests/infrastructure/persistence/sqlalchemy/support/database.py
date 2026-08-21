from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from subscription.infrastructure.persistence.sqlalchemy import AsyncSessionFactory, SubscriptionBase


class SqliteTestDatabase:
    def __init__(self) -> None:
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        self.session_maker = async_sessionmaker(self.engine, expire_on_commit=False)

    async def create_schema(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(SubscriptionBase.metadata.create_all)

    async def dispose(self) -> None:
        await self.engine.dispose()

    def session_factory(self) -> AsyncSessionFactory:
        @asynccontextmanager
        async def factory() -> AsyncIterator[AsyncSession]:
            async with self.session_maker() as session:
                yield session

        return factory
