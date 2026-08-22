"""Tests for IntegrationClient."""

from integration_auth.domain.entities.integration_client import IntegrationClient
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission


def test_client_keeps_machine_identity_and_authorization_grants() -> None:
    client = IntegrationClient(
        client_id=IntegrationClientId("client-123"),
        permissions=frozenset({Permission("catalog.read"), Permission("orders.read")}),
        scopes=frozenset({IntegrationScope("store", "store-123")}),
    )

    assert client.client_id == IntegrationClientId("client-123")
    assert Permission("catalog.read") in client.permissions
    assert IntegrationScope("store", "store-123") in client.scopes


def test_client_defaults_to_no_authorization_grants() -> None:
    client = IntegrationClient(client_id=IntegrationClientId("client-123"))

    assert client.permissions == frozenset()
    assert client.scopes == frozenset()
