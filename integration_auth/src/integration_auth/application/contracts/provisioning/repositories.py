"""Provisioning persistence contracts."""

from typing import Protocol

from integration_auth.application.security.protected_credential_secret import (
    ProtectedCredentialSecret,
)
from integration_auth.domain.entities.integration_client import IntegrationClient
from integration_auth.domain.entities.integration_credential import IntegrationCredential
from integration_auth.domain.value_objects.identifiers import (
    IntegrationClientId,
    IntegrationCredentialId,
)


class IntegrationClientProvisioningRepository(Protocol):
    """Persist integration client lifecycle changes."""

    async def get_by_id(self, client_id: IntegrationClientId) -> IntegrationClient | None: ...

    async def add(self, client: IntegrationClient) -> None: ...

    async def update(self, client: IntegrationClient) -> None: ...


class IntegrationCredentialProvisioningRepository(Protocol):
    """Persist credential lifecycle and protected secret material."""

    async def get_by_id(
        self,
        credential_id: IntegrationCredentialId,
    ) -> IntegrationCredential | None: ...

    async def list_for_client(
        self,
        client_id: IntegrationClientId,
    ) -> tuple[IntegrationCredential, ...]: ...

    async def add(
        self,
        credential: IntegrationCredential,
        protected_secret: ProtectedCredentialSecret,
    ) -> None: ...

    async def update(self, credential: IntegrationCredential) -> None: ...

    async def rotate(
        self,
        *,
        previous_credentials: tuple[IntegrationCredential, ...],
        new_credential: IntegrationCredential,
        protected_secret: ProtectedCredentialSecret,
    ) -> None:
        """Atomically persist rotation metadata and protected secret material."""
        ...
