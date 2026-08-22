"""Update integration client authorization grants."""

from dataclasses import replace

from integration_auth.application.contracts.provisioning.repositories import (
    IntegrationClientProvisioningRepository,
)
from integration_auth.application.errors.provisioning import ProvisioningClientNotFoundError
from integration_auth.domain.entities.integration_client import IntegrationClient
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.domain.value_objects.integration_scope import IntegrationScope
from integration_auth.domain.value_objects.permission import Permission


class UpdateIntegrationClientGrantsService:
    """Replace an integration client's permission and scope grants."""

    def __init__(self, repository: IntegrationClientProvisioningRepository) -> None:
        self._repository = repository

    async def update(
        self,
        *,
        client_id: IntegrationClientId,
        permissions: frozenset[Permission],
        scopes: frozenset[IntegrationScope],
    ) -> IntegrationClient:
        client = await self._repository.get_by_id(client_id)
        if client is None:
            raise ProvisioningClientNotFoundError("integration client was not found")

        updated = replace(client, permissions=permissions, scopes=scopes)
        await self._repository.update(updated)
        return updated
