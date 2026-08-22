"""Tests for host-owned composition of authentication principals."""

from multi_auth_host_consumer_app import HostActorKind
from multi_auth_host_consumer_app.composition import HostActorFactory
from multi_auth_host_consumer_app.mappers import IdentityActorMapper, IntegrationActorMapper
from tests.support.principal_builders import IdentityPrincipalBuilder, IntegrationPrincipalBuilder


def test_host_actor_factory_composes_both_authentication_sources() -> None:
    factory = HostActorFactory(
        identity_mapper=IdentityActorMapper(),
        integration_mapper=IntegrationActorMapper(),
    )

    human = factory.from_identity(IdentityPrincipalBuilder().build())
    integration = factory.from_integration(IntegrationPrincipalBuilder().build())

    assert human.kind is HostActorKind.HUMAN
    assert integration.kind is HostActorKind.INTEGRATION
    assert human.actor_id.startswith("user:")
    assert integration.actor_id == "integration:client-123"
