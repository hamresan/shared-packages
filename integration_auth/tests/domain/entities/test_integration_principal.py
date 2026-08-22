"""Tests for IntegrationPrincipal."""

from integration_auth.domain.entities.integration_principal import IntegrationPrincipal
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission


def test_principal_represents_authenticated_machine_authorization_facts() -> None:
    principal = IntegrationPrincipal(
        client_id=IntegrationClientId("client-123"),
        permissions=frozenset({Permission("orders.read")}),
        scopes=frozenset({IntegrationScope("store", "store-123")}),
    )

    assert principal.client_id == IntegrationClientId("client-123")
    assert principal.permissions == frozenset({Permission("orders.read")})
    assert principal.scopes == frozenset({IntegrationScope("store", "store-123")})


def test_principal_defaults_to_no_authorization_facts() -> None:
    principal = IntegrationPrincipal(client_id=IntegrationClientId("client-123"))

    assert principal.permissions == frozenset()
    assert principal.scopes == frozenset()
