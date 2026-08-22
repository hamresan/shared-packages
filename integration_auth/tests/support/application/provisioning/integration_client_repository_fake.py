"""In-memory integration client provisioning repository fake."""

from integration_auth.application.contracts.provisioning.repositories import (
    IntegrationClientProvisioningRepository,
)
from integration_auth.domain.entities.integration_client import IntegrationClient
from integration_auth.domain.value_objects.identifiers import IntegrationClientId


class IntegrationClientProvisioningRepositoryFake(IntegrationClientProvisioningRepository):
    """Store integration clients in memory for provisioning tests."""

    def __init__(self, clients: tuple[IntegrationClient, ...] = ()) -> None:
        self._clients = {client.client_id: client for client in clients}
        self.added: list[IntegrationClient] = []
        self.updated: list[IntegrationClient] = []

    async def get_by_id(self, client_id: IntegrationClientId) -> IntegrationClient | None:
        return self._clients.get(client_id)

    async def add(self, client: IntegrationClient) -> None:
        self._clients[client.client_id] = client
        self.added.append(client)

    async def update(self, client: IntegrationClient) -> None:
        self._clients[client.client_id] = client
        self.updated.append(client)
