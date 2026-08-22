"""Register integration clients."""

from integration_auth.application.contracts.provisioning.id_generators import (
    IntegrationClientIdGenerator,
)
from integration_auth.application.contracts.provisioning.repositories import (
    IntegrationClientProvisioningRepository,
)
from integration_auth.domain.entities.integration_client import IntegrationClient
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission


class RegisterIntegrationClientService:
    """Create and persist a new integration client."""

    def __init__(
        self,
        *,
        client_id_generator: IntegrationClientIdGenerator,
        repository: IntegrationClientProvisioningRepository,
    ) -> None:
        self._client_id_generator = client_id_generator
        self._repository = repository

    async def register(
        self,
        *,
        permissions: frozenset[Permission] = frozenset(),
        scopes: frozenset[IntegrationScope] = frozenset(),
    ) -> IntegrationClient:
        client = IntegrationClient(
            client_id=self._client_id_generator.generate(),
            permissions=permissions,
            scopes=scopes,
        )
        await self._repository.add(client)
        return client
