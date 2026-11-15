from collections.abc import AsyncGenerator
from dataclasses import dataclass
from uuid import UUID

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from business.bootstrap import BusinessApplicationFactory
from business.infrastructure.clock import SystemClock
from business.infrastructure.identifiers import UuidIdentifierGenerator
from business.presentation import build_fastapi_business_adapter
from tests.support.builders import OTHER_USER_ID, TEST_USER_ID
from tests.support.http_authentication import TestAuthenticatedActorDependency
from tests.support.sqlalchemy_environment import SqlAlchemyEnvironment


@dataclass(slots=True)
class HttpEnvironment:
    client: AsyncClient
    owner_id: UUID
    other_id: UUID


@pytest.fixture
async def business_http_environment(
    sqlalchemy_environment: SqlAlchemyEnvironment,
) -> AsyncGenerator[HttpEnvironment]:
    identity = TestAuthenticatedActorDependency(
        {"owner-token": TEST_USER_ID, "member-token": OTHER_USER_ID}
    )
    factory = BusinessApplicationFactory(
        sqlalchemy_environment.uow, SystemClock(), UuidIdentifierGenerator()
    )
    adapter = build_fastapi_business_adapter(
        authenticated_actor_dependency=identity,
        businesses=factory.businesses(),
        branches=factory.branches(),
        memberships=factory.memberships(),
    )
    app = FastAPI()
    adapter.install(app)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield HttpEnvironment(client, TEST_USER_ID, OTHER_USER_ID)
