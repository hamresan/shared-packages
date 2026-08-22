"""Tests for exact permission authorization."""

from integration_auth.domain.policies.permission_requirement_policy import PermissionRequirementPolicy
from integration_auth.domain.value_objects.permission import Permission
from tests.support.application.authorization.authorization_principal_builder import (
    AuthorizationPrincipalBuilder,
)


def test_allows_exact_permission_grant() -> None:
    builder = AuthorizationPrincipalBuilder()
    builder.permissions = frozenset({Permission("orders.read")})
    principal = builder.build()

    assert PermissionRequirementPolicy().allows(
        principal=principal,
        permission=Permission("orders.read"),
    )


def test_denies_missing_permission_without_implicit_inheritance() -> None:
    builder = AuthorizationPrincipalBuilder()
    builder.permissions = frozenset({Permission("orders.read")})
    principal = builder.build()

    assert not PermissionRequirementPolicy().allows(
        principal=principal,
        permission=Permission("orders.write"),
    )
