"""Credential verification-secret provider fake."""

from integration_auth.application.contracts.authentication.credential_secret_provider import (
    CredentialSecretProvider,
)
from integration_auth.domain.value_objects.identifiers import IntegrationCredentialId


class CredentialSecretProviderFake(CredentialSecretProvider):
    """Return deterministic secrets keyed by credential identifier."""

    def __init__(self, secrets: dict[IntegrationCredentialId, bytes]) -> None:
        self._secrets = secrets

    async def get_verification_secret(
        self,
        credential_id: IntegrationCredentialId,
    ) -> bytes | None:
        return self._secrets.get(credential_id)
