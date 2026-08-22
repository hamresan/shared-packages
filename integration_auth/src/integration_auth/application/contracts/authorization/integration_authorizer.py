"""Application authorization use-case contract."""

from typing import Protocol

from integration_auth.domain.entities.integration_principal import IntegrationPrincipal
from integration_auth.domain.value_objects.integration_resource import IntegrationResource
from integration_auth.domain.value_objects.permission import Permission


class IntegrationRequestAuthorizer(Protocol):
    """Require one permission and optional resource scope for an integration principal."""

    def require(
        self,
        *,
        principal: IntegrationPrincipal,
        permission: Permission,
        resource: IntegrationResource | None = None,
    ) -> None: ...
