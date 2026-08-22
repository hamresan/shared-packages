"""Tests for exact permission authorization."""

from integration_auth.domain.policies import PermissionRequirementPolicy
from integration_auth.domain.value_objects import Permission
from tests.support.application.authorization import (
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
