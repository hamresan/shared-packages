"""Tests for host mapping of machine integration principals."""

from multi_auth_host_consumer_app import HostActorKind
from multi_auth_host_consumer_app.mappers import IntegrationActorMapper
from tests.support.principal_builders import IntegrationPrincipalBuilder


def test_integration_principal_maps_authorization_facts_to_host_actor() -> None:
    principal = IntegrationPrincipalBuilder().build()

    actor = IntegrationActorMapper().map(principal)

    assert actor.actor_id == "integration:client-123"
    assert actor.kind is HostActorKind.INTEGRATION
    assert actor.authentication_method == "hmac-sha256"
    assert actor.permissions == frozenset({"orders.read", "catalog.read"})
    assert actor.resource_scopes == frozenset({"store:store-123"})
