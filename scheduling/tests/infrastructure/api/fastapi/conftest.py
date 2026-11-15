"""Exercise HTTP flows through both persistence adapter implementations."""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from scheduling.infrastructure.persistence.sqlalchemy import (
    CalendarPersistenceMapper,
    SqlAlchemyCalendarRepositoryFactory,
    SqlAlchemyCalendarUnitOfWorkFactory,
)
from tests.support.api.host_factory import HttpTestHost, build_http_test_host
from tests.support.persistence import InMemoryCalendarStore, InMemoryCalendarUnitOfWorkFactory
from tests.support.persistence.sqlalchemy_database import sqlite_engine, sqlite_session_factory

__all__ = ["sqlite_engine", "sqlite_session_factory"]


@pytest.fixture(params=["memory", "sqlalchemy"])
def http_host(
    request: pytest.FixtureRequest,
    sqlite_session_factory: async_sessionmaker[AsyncSession],
) -> HttpTestHost:
    if request.param == "memory":
        return build_http_test_host(InMemoryCalendarUnitOfWorkFactory(InMemoryCalendarStore()))
    return build_http_test_host(
        SqlAlchemyCalendarUnitOfWorkFactory(
            sqlite_session_factory,
            SqlAlchemyCalendarRepositoryFactory(CalendarPersistenceMapper()),
        )
    )


@pytest.fixture
async def client(http_host: HttpTestHost) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=http_host.app), base_url="http://test"
    ) as client:
        yield client
