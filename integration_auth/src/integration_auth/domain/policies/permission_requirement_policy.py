"""Exact permission requirement policy."""

from integration_auth.domain.entities.integration_principal import IntegrationPrincipal
from integration_auth.domain.value_objects.permission import Permission


class PermissionRequirementPolicy:
    """Require an exact permission grant on the authenticated principal."""

    def allows(self, *, principal: IntegrationPrincipal, permission: Permission) -> bool:
        return permission in principal.permissions
