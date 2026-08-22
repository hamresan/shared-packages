"""Test factory for IntegrationAuthorizer."""

from integration_auth.application.services.authorization import (
    IntegrationAuthorizer,
)
from integration_auth.domain.policies import (
    PermissionRequirementPolicy,
    ResourceScopeAuthorizationPolicy,
)


def build_authorizer() -> IntegrationAuthorizer:
    """Build the real authorizer with real authorization policies."""
    return IntegrationAuthorizer(
        permission_policy=PermissionRequirementPolicy(),
        resource_scope_policy=ResourceScopeAuthorizationPolicy(),
    )
