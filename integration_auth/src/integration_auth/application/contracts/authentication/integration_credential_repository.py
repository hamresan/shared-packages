"""Integration credential repository contract."""

from typing import Protocol

from integration_auth.domain.entities.integration_credential import IntegrationCredential
from integration_auth.domain.value_objects.identifiers import IntegrationClientId


class IntegrationCredentialRepository(Protocol):
    """Load credential candidates for one integration client."""

    async def list_for_client(
        self,
        client_id: IntegrationClientId,
    ) -> tuple[IntegrationCredential, ...]: ...
