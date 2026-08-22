"""Credential verification-secret provider contract."""

from typing import Protocol

from integration_auth.domain.value_objects.identifiers import IntegrationCredentialId


class CredentialSecretProvider(Protocol):
    """Provide transient verification material for a credential."""

    async def get_verification_secret(
        self,
        credential_id: IntegrationCredentialId,
    ) -> bytes | None: ...
