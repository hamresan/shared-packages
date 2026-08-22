"""Tests for the SQLAlchemy integration-client repository."""

import asyncio
from pathlib import Path

from integration_auth.domain.entities.integration_client import IntegrationClient
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission
from integration_auth.infrastructure.persistence.sqlalchemy.mappers.client_mapper import (
    IntegrationClientRecordMapper,
)
from integration_auth.infrastructure.persistence.sqlalchemy.repositories.client_repository import (
    SqlAlchemyIntegrationClientRepository,
)
from tests.support.infrastructure.persistence.sqlalchemy.database import SqlAlchemyTestDatabase


def test_client_repository_round_trips_and_updates_grants(tmp_path: Path) -> None:
    async def run() -> None:
        database = SqlAlchemyTestDatabase(tmp_path / "clients.db")
        await database.create_schema()
        repository = SqlAlchemyIntegrationClientRepository(
            database.session_factory,
            IntegrationClientRecordMapper(),
        )
        client_id = IntegrationClientId("client-123")
        original = IntegrationClient(
            client_id=client_id,
            permissions=frozenset({Permission("catalog.read")}),
            scopes=frozenset({IntegrationScope("store", "store-1")}),
        )
        await repository.add(original)
        assert await repository.get_by_id(client_id) == original

        updated = IntegrationClient(
            client_id=client_id,
            permissions=frozenset({Permission("orders.read")}),
            scopes=frozenset({IntegrationScope("store", "store-2")}),
        )
        await repository.update(updated)
        assert await repository.get_by_id(client_id) == updated
        assert await repository.get_by_id(IntegrationClientId("missing-client")) is None
        await database.dispose()

    asyncio.run(run())
