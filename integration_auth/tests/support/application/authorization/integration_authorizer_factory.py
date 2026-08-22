"""Test factory for IntegrationAuthorizer."""

from integration_auth.application.services.authorization.integration_authorizer import (
    IntegrationAuthorizer,
)
from integration_auth.domain.policies.permission_requirement_policy import PermissionRequirementPolicy
from integration_auth.domain.policies.resource_scope_authorization_policy import (
    ResourceScopeAuthorizationPolicy,
)


def build_authorizer() -> IntegrationAuthorizer:
    """Build the real authorizer with real authorization policies."""
    return IntegrationAuthorizer(
        permission_policy=PermissionRequirementPolicy(),
        resource_scope_policy=ResourceScopeAuthorizationPolicy(),
    )
