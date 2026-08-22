"""Tests for downstream service independence from authentication packages."""

from multi_auth_host_consumer_app.mappers import IdentityActorMapper, IntegrationActorMapper
from multi_auth_host_consumer_app.services import ActorDescriptionService
from tests.support.principal_builders import IdentityPrincipalBuilder, IntegrationPrincipalBuilder


def test_downstream_service_accepts_human_actor_without_identity_dependency() -> None:
    actor = IdentityActorMapper().map(IdentityPrincipalBuilder().build())

    result = ActorDescriptionService().describe(actor)

    assert result["kind"] == "human"
    assert result["permissions"] == []
    assert result["resource_scopes"] == []


def test_downstream_service_accepts_integration_actor_without_integration_auth_dependency() -> None:
    actor = IntegrationActorMapper().map(IntegrationPrincipalBuilder().build())

    result = ActorDescriptionService().describe(actor)

    assert result["kind"] == "integration"
    assert result["permissions"] == ["catalog.read", "orders.read"]
    assert result["resource_scopes"] == ["store:store-123"]
