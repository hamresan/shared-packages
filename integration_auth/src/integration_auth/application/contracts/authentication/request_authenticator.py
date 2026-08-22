"""Application authentication use-case contract."""

from typing import Protocol

from integration_auth.application.dto.authentication import AuthenticateIntegrationRequest
from integration_auth.domain.entities.integration_principal import IntegrationPrincipal


class IntegrationRequestAuthenticator(Protocol):
    """Authenticate one integration request."""

    async def authenticate(
        self,
        authentication_request: AuthenticateIntegrationRequest,
    ) -> IntegrationPrincipal: ...
