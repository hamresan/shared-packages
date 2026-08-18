from collections.abc import AsyncGenerator, MutableMapping
from contextlib import asynccontextmanager
from typing import Literal

from identity.migrations import identity_metadata, include_identity_name
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool
from store.migrations import include_store_name, store_metadata

AlembicObjectType = Literal[
    "schema",
    "table",
    "column",
    "index",
    "unique_constraint",
    "foreign_key_constraint",
    "check_constraint",
]
AlembicParentNames = MutableMapping[
    Literal["schema_name", "table_name", "schema_qualified_table_name"],
    str | None,
]


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
            await connection.run_sync(identity_metadata().create_all)
            await connection.run_sync(store_metadata().create_all)

    async def close(self) -> None:
        await self.engine.dispose()


def consumer_metadata() -> tuple[MetaData, MetaData]:
    return identity_metadata(), store_metadata()


def include_consumer_name(
    name: str | None,
    type_: AlembicObjectType,
    parent_names: AlembicParentNames,
) -> bool:
    return include_identity_name(name, type_, parent_names) or include_store_name(
        name,
        type_,
        parent_names,
    )
