from collections.abc import Sequence

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from subscription.migrations import subscription_metadata


class ConsumerDatabase:
    def __init__(self, url: str) -> None:
        self.engine: AsyncEngine = create_async_engine(url)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def create_schema(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(subscription_metadata().create_all)

    async def dispose(self) -> None:
        await self.engine.dispose()


def consumer_metadata() -> Sequence[MetaData]:
    return (subscription_metadata(),)


def build_session_factory(database: ConsumerDatabase) -> async_sessionmaker[AsyncSession]:
    return database.session_factory
