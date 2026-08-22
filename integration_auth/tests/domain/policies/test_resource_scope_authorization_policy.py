"""Tests for exact resource-scope authorization."""

from integration_auth.domain.policies.resource_scope_authorization_policy import (
    ResourceScopeAuthorizationPolicy,
)
from integration_auth.domain.value_objects.integration_resource import IntegrationResource
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from tests.support.application.authorization.authorization_principal_builder import (
    AuthorizationPrincipalBuilder,
)


def test_allows_exact_resource_scope() -> None:
    builder = AuthorizationPrincipalBuilder()
    builder.scopes = frozenset({IntegrationScope("store", "store-123")})
    principal = builder.build()

    assert ResourceScopeAuthorizationPolicy().allows(
        principal=principal,
        resource=IntegrationResource("store", "store-123"),
    )


def test_denies_different_resource_id() -> None:
    builder = AuthorizationPrincipalBuilder()
    builder.scopes = frozenset({IntegrationScope("store", "store-123")})
    principal = builder.build()

    assert not ResourceScopeAuthorizationPolicy().allows(
        principal=principal,
        resource=IntegrationResource("store", "store-456"),
    )


def test_denies_different_resource_type() -> None:
    builder = AuthorizationPrincipalBuilder()
    builder.scopes = frozenset({IntegrationScope("store", "same-id")})
    principal = builder.build()

    assert not ResourceScopeAuthorizationPolicy().allows(
        principal=principal,
        resource=IntegrationResource("organization", "same-id"),
    )
