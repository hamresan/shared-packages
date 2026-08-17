from dataclasses import dataclass

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from store.infrastructure.persistence.sqlalchemy import StoreBase


@dataclass(slots=True)
class SqliteStorePersistence:
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]

    @classmethod
    async def create(cls) -> "SqliteStorePersistence":
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as connection:
            await connection.run_sync(StoreBase.metadata.create_all)
        return cls(
            engine=engine,
            session_factory=async_sessionmaker(engine, expire_on_commit=False),
        )

    async def close(self) -> None:
        await self.engine.dispose()
