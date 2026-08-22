"""Tests for IntegrationAuthorizer."""

import pytest

from integration_auth.application.dto.authorization.authorization_result import (
    AuthorizationDecisionReason,
)
from integration_auth.application.errors.authorization import IntegrationAuthorizationError
from integration_auth.domain.value_objects.integration_resource import IntegrationResource
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission
from tests.support.application.authorization.authorization_principal_builder import (
    AuthorizationPrincipalBuilder,
)
from tests.support.application.authorization.integration_authorizer_factory import build_authorizer


def test_allows_route_level_permission_without_resource_scope() -> None:
    builder = AuthorizationPrincipalBuilder()
    builder.permissions = frozenset({Permission("catalog.write")})

    result = build_authorizer().authorize(
        principal=builder.build(),
        permission=Permission("catalog.write"),
    )

    assert result.allowed
    assert result.reason is AuthorizationDecisionReason.ALLOWED


def test_denies_missing_permission_before_resource_scope_check() -> None:
    builder = AuthorizationPrincipalBuilder()
    builder.scopes = frozenset({IntegrationScope("store", "store-123")})

    result = build_authorizer().authorize(
        principal=builder.build(),
        permission=Permission("orders.read"),
        resource=IntegrationResource("store", "store-123"),
    )

    assert not result.allowed
    assert result.reason is AuthorizationDecisionReason.MISSING_PERMISSION


def test_allows_permission_and_matching_resource_scope() -> None:
    builder = AuthorizationPrincipalBuilder()
    builder.permissions = frozenset({Permission("orders.read")})
    builder.scopes = frozenset({IntegrationScope("store", "store-123")})

    result = build_authorizer().authorize(
        principal=builder.build(),
        permission=Permission("orders.read"),
        resource=IntegrationResource("store", "store-123"),
    )

    assert result.allowed


def test_denies_matching_permission_without_resource_scope() -> None:
    builder = AuthorizationPrincipalBuilder()
    builder.permissions = frozenset({Permission("orders.read")})

    result = build_authorizer().authorize(
        principal=builder.build(),
        permission=Permission("orders.read"),
        resource=IntegrationResource("store", "store-123"),
    )

    assert not result.allowed
    assert result.reason is AuthorizationDecisionReason.MISSING_RESOURCE_SCOPE


def test_require_returns_none_when_authorized() -> None:
    builder = AuthorizationPrincipalBuilder()
    builder.permissions = frozenset({Permission("catalog.read")})

    assert (
        build_authorizer().require(
            principal=builder.build(),
            permission=Permission("catalog.read"),
        )
        is None
    )


def test_require_raises_authorization_error_with_stable_reason() -> None:
    builder = AuthorizationPrincipalBuilder()

    with pytest.raises(IntegrationAuthorizationError) as error:
        build_authorizer().require(
            principal=builder.build(),
            permission=Permission("orders.read"),
        )

    assert error.value.reason is AuthorizationDecisionReason.MISSING_PERMISSION
