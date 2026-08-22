"""Tests for integration-client persistence mapping."""

from integration_auth.domain.entities.integration_client import IntegrationClient
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission
from integration_auth.infrastructure.persistence.sqlalchemy.mappers.client_mapper import (
    IntegrationClientRecordMapper,
)


def test_client_mapper_round_trips_domain_grants() -> None:
    mapper = IntegrationClientRecordMapper()
    client = IntegrationClient(
        client_id=IntegrationClientId("client-123"),
        permissions=frozenset({Permission("orders.read"), Permission("catalog.read")}),
        scopes=frozenset({IntegrationScope("store", "store-1")}),
    )

    record = mapper.to_record(client)

    assert record.permissions == ["catalog.read", "orders.read"]
    assert mapper.to_domain(record) == client
