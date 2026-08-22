"""Integration client repository fake."""

from integration_auth.application.contracts.authentication.integration_client_repository import (
    IntegrationClientRepository,
)
from integration_auth.domain.entities.integration_client import IntegrationClient
from integration_auth.domain.value_objects.identifiers import IntegrationClientId


class IntegrationClientRepositoryFake(IntegrationClientRepository):
    """Return one configured integration client."""

    def __init__(self, client: IntegrationClient | None) -> None:
        self._client = client

    async def get_by_id(self, client_id: IntegrationClientId) -> IntegrationClient | None:
        if self._client is None or self._client.client_id != client_id:
            return None
        return self._client
