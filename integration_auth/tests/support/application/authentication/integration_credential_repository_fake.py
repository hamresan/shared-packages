"""Integration credential repository fake."""

from integration_auth.application.contracts.authentication.integration_credential_repository import (
    IntegrationCredentialRepository,
)
from integration_auth.domain.entities.integration_credential import IntegrationCredential
from integration_auth.domain.value_objects.identifiers import IntegrationClientId


class IntegrationCredentialRepositoryFake(IntegrationCredentialRepository):
    """Return configured credential candidates for tests."""

    def __init__(self, credentials: tuple[IntegrationCredential, ...]) -> None:
        self._credentials = credentials

    async def list_for_client(
        self,
        client_id: IntegrationClientId,
    ) -> tuple[IntegrationCredential, ...]:
        return self._credentials
