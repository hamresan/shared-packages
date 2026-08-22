from collections.abc import MutableMapping, Sequence
from typing import Literal

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from subscription.migrations import include_subscription_name, subscription_metadata

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


def include_consumer_name(
    name: str | None,
    type_: AlembicObjectType,
    parent_names: AlembicParentNames,
) -> bool:
    package_parent_names: dict[str, str | None] = {
        str(key): value for key, value in parent_names.items()
    }
    return include_subscription_name(name, type_, package_parent_names)


def build_session_factory(database: ConsumerDatabase) -> async_sessionmaker[AsyncSession]:
    return database.session_factory
