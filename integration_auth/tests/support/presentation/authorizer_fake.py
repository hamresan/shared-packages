"""Authorization fake for FastAPI presentation tests."""

from integration_auth.application.contracts.authorization import IntegrationRequestAuthorizer
from integration_auth.domain.entities.integration_principal import IntegrationPrincipal
from integration_auth.domain.value_objects.integration_resource import IntegrationResource
from integration_auth.domain.value_objects.permission import Permission


class IntegrationRequestAuthorizerFake(IntegrationRequestAuthorizer):
    """Record authorization requirements and optionally raise a configured error."""

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.requirements: list[
            tuple[IntegrationPrincipal, Permission, IntegrationResource | None]
        ] = []

    def require(
        self,
        *,
        principal: IntegrationPrincipal,
        permission: Permission,
        resource: IntegrationResource | None = None,
    ) -> None:
        self.requirements.append((principal, permission, resource))
        if self.error is not None:
            raise self.error
