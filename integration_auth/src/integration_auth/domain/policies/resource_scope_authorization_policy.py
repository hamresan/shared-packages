"""Exact resource-scope authorization policy."""

from integration_auth.domain.entities.integration_principal import IntegrationPrincipal
from integration_auth.domain.value_objects.integration_resource import IntegrationResource


class ResourceScopeAuthorizationPolicy:
    """Require an exact scope grant for a target resource."""

    def allows(
        self,
        *,
        principal: IntegrationPrincipal,
        resource: IntegrationResource,
    ) -> bool:
        return any(
            scope.resource_type == resource.resource_type
            and scope.resource_id == resource.resource_id
            for scope in principal.scopes
        )
