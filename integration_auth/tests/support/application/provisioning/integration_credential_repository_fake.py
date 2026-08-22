"""In-memory integration credential provisioning repository fake."""

from integration_auth.application.contracts.provisioning.repositories import (
    IntegrationCredentialProvisioningRepository,
)
from integration_auth.application.security.protected_credential_secret import (
    ProtectedCredentialSecret,
)
from integration_auth.domain.entities.integration_credential import IntegrationCredential
from integration_auth.domain.value_objects.identifiers import (
    IntegrationClientId,
    IntegrationCredentialId,
)


class IntegrationCredentialProvisioningRepositoryFake(IntegrationCredentialProvisioningRepository):
    """Store credential metadata and protected material for provisioning tests."""

    def __init__(self, credentials: tuple[IntegrationCredential, ...] = ()) -> None:
        self._credentials = {credential.credential_id: credential for credential in credentials}
        self.added: list[tuple[IntegrationCredential, ProtectedCredentialSecret]] = []
        self.updated: list[IntegrationCredential] = []
        self.rotations: list[
            tuple[
                tuple[IntegrationCredential, ...],
                IntegrationCredential,
                ProtectedCredentialSecret,
            ]
        ] = []

    async def get_by_id(
        self,
        credential_id: IntegrationCredentialId,
    ) -> IntegrationCredential | None:
        return self._credentials.get(credential_id)

    async def list_for_client(
        self,
        client_id: IntegrationClientId,
    ) -> tuple[IntegrationCredential, ...]:
        return tuple(
            credential
            for credential in self._credentials.values()
            if credential.client_id == client_id
        )

    async def add(
        self,
        credential: IntegrationCredential,
        protected_secret: ProtectedCredentialSecret,
    ) -> None:
        self._credentials[credential.credential_id] = credential
        self.added.append((credential, protected_secret))

    async def update(self, credential: IntegrationCredential) -> None:
        self._credentials[credential.credential_id] = credential
        self.updated.append(credential)

    async def rotate(
        self,
        *,
        previous_credentials: tuple[IntegrationCredential, ...],
        new_credential: IntegrationCredential,
        protected_secret: ProtectedCredentialSecret,
    ) -> None:
        for credential in previous_credentials:
            self._credentials[credential.credential_id] = credential
        self._credentials[new_credential.credential_id] = new_credential
        self.rotations.append((previous_credentials, new_credential, protected_secret))
