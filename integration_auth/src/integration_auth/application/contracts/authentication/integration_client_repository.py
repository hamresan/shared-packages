"""Integration client repository contract."""

from typing import Protocol

from integration_auth.domain.entities.integration_client import IntegrationClient
from integration_auth.domain.value_objects.identifiers import IntegrationClientId


class IntegrationClientRepository(Protocol):
    """Load integration clients for authentication."""

    async def get_by_id(self, client_id: IntegrationClientId) -> IntegrationClient | None: ...
