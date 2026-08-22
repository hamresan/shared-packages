"""Framework-neutral integration authorization service."""

from integration_auth.application.dto.authorization import (
    AuthorizationDecisionReason,
    AuthorizationResult,
)
from integration_auth.application.errors import IntegrationAuthorizationError
from integration_auth.domain.entities import IntegrationPrincipal
from integration_auth.domain.policies import (
    PermissionRequirementPolicy,
    ResourceScopeAuthorizationPolicy,
)
from integration_auth.domain.value_objects import IntegrationResource, Permission


class IntegrationAuthorizer:
    """Authorize authenticated integrations by permission and optional resource scope."""

    def __init__(
        self,
        *,
        permission_policy: PermissionRequirementPolicy,
        resource_scope_policy: ResourceScopeAuthorizationPolicy,
    ) -> None:
        self._permission_policy = permission_policy
        self._resource_scope_policy = resource_scope_policy

    def authorize(
        self,
        *,
        principal: IntegrationPrincipal,
        permission: Permission,
        resource: IntegrationResource | None = None,
    ) -> AuthorizationResult:
        if not self._permission_policy.allows(
            principal=principal,
            permission=permission,
        ):
            return AuthorizationResult.deny(AuthorizationDecisionReason.MISSING_PERMISSION)

        if resource is not None and not self._resource_scope_policy.allows(
            principal=principal,
            resource=resource,
        ):
            return AuthorizationResult.deny(AuthorizationDecisionReason.MISSING_RESOURCE_SCOPE)

        return AuthorizationResult.allow()

    def require(
        self,
        *,
        principal: IntegrationPrincipal,
        permission: Permission,
        resource: IntegrationResource | None = None,
    ) -> None:
        result = self.authorize(
            principal=principal,
            permission=permission,
            resource=resource,
        )
        if not result.allowed:
            raise IntegrationAuthorizationError(result.reason)
