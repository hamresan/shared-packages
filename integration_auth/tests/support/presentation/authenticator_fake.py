"""Authentication fake for FastAPI presentation tests."""

from integration_auth.application.contracts.authentication import IntegrationRequestAuthenticator
from integration_auth.application.dto.authentication import AuthenticateIntegrationRequest
from integration_auth.domain.entities.integration_principal import IntegrationPrincipal


class IntegrationRequestAuthenticatorFake(IntegrationRequestAuthenticator):
    """Record authentication requests and return or raise configured behavior."""

    def __init__(
        self,
        *,
        principal: IntegrationPrincipal,
        error: Exception | None = None,
    ) -> None:
        self.principal = principal
        self.error = error
        self.requests: list[AuthenticateIntegrationRequest] = []

    async def authenticate(
        self,
        authentication_request: AuthenticateIntegrationRequest,
    ) -> IntegrationPrincipal:
        self.requests.append(authentication_request)
        if self.error is not None:
            raise self.error
        return self.principal
