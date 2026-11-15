from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from business.migrations import business_metadata
from identity.migrations import identity_metadata
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


class ConsumerDatabase:
    def __init__(self) -> None:
        self.engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool)
        self.session_maker = async_sessionmaker(self.engine, expire_on_commit=False)

    @asynccontextmanager
    async def session_factory(self) -> AsyncGenerator[AsyncSession]:
        async with self.session_maker() as session:
            yield session

    async def create_schema(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(identity_metadata().create_all)
            await connection.run_sync(business_metadata().create_all)

    async def close(self) -> None:
        await self.engine.dispose()
