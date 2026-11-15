from collections.abc import AsyncGenerator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from business.infrastructure.persistence.sqlalchemy import (
    BranchMapper,
    BusinessBase,
    BusinessMapper,
    MembershipAuditMapper,
    MembershipMapper,
    SqlAlchemyBusinessUnitOfWorkFactory,
)


@dataclass(frozen=True, slots=True)
class SqlAlchemyEnvironment:
    engine: AsyncEngine
    uow: SqlAlchemyBusinessUnitOfWorkFactory


@pytest.fixture
async def sqlalchemy_environment(tmp_path: Path) -> AsyncGenerator[SqlAlchemyEnvironment]:
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'business.sqlite'}")

    @event.listens_for(engine.sync_engine, "connect")
    def enable_foreign_keys(dbapi_connection: Any, connection_record: object) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as connection:
        await connection.run_sync(BusinessBase.metadata.create_all)
    factory = SqlAlchemyBusinessUnitOfWorkFactory(
        async_sessionmaker(engine, expire_on_commit=False),
        BusinessMapper(),
        BranchMapper(),
        MembershipMapper(),
        MembershipAuditMapper(),
    )
    yield SqlAlchemyEnvironment(engine, factory)
    await engine.dispose()
