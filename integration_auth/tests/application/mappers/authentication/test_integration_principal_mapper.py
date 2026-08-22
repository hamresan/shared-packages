"""Tests for IntegrationPrincipalMapper."""

from integration_auth.application.mappers.authentication.integration_principal_mapper import (
    IntegrationPrincipalMapper,
)
from integration_auth.domain.entities.integration_client import IntegrationClient
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission


def test_maps_client_identity_and_grants_to_principal() -> None:
    client = IntegrationClient(
        client_id=IntegrationClientId("client-123"),
        permissions=frozenset({Permission("orders.read")}),
        scopes=frozenset({IntegrationScope("store", "store-123")}),
    )

    principal = IntegrationPrincipalMapper().from_client(client)

    assert principal.client_id == client.client_id
    assert principal.permissions == client.permissions
    assert principal.scopes == client.scopes
