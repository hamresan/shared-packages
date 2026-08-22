"""Tests for host mapping of human identity principals."""

from multi_auth_host_consumer_app import HostActorKind
from multi_auth_host_consumer_app.mappers import IdentityActorMapper
from tests.support.principal_builders import IdentityPrincipalBuilder


def test_identity_principal_maps_to_human_host_actor() -> None:
    principal = IdentityPrincipalBuilder().build()

    actor = IdentityActorMapper().map(principal)

    assert actor.actor_id == f"user:{principal.user_id}"
    assert actor.kind is HostActorKind.HUMAN
    assert actor.authentication_method == "otp"
    assert actor.permissions == frozenset()
    assert actor.resource_scopes == frozenset()
