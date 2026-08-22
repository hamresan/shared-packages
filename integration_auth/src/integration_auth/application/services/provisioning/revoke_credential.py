"""Revoke integration credentials."""

from integration_auth.application.contracts.authentication.clock import Clock
from integration_auth.application.contracts.provisioning.repositories import (
    IntegrationCredentialProvisioningRepository,
)
from integration_auth.application.errors.provisioning import ProvisioningCredentialNotFoundError
from integration_auth.application.mappers.time.unix_timestamp_mapper import UnixTimestampMapper
from integration_auth.domain.entities.integration_credential import IntegrationCredential
from integration_auth.domain.services.credential_lifecycle_transitioner import (
    CredentialLifecycleTransitioner,
)
from integration_auth.domain.value_objects.identifiers import IntegrationCredentialId


class RevokeCredentialService:
    """Revoke one credential through the lifecycle transition boundary."""

    def __init__(
        self,
        *,
        repository: IntegrationCredentialProvisioningRepository,
        transitioner: CredentialLifecycleTransitioner,
        clock: Clock,
        timestamp_mapper: UnixTimestampMapper,
    ) -> None:
        self._repository = repository
        self._transitioner = transitioner
        self._clock = clock
        self._timestamp_mapper = timestamp_mapper

    async def revoke(self, credential_id: IntegrationCredentialId) -> IntegrationCredential:
        credential = await self._repository.get_by_id(credential_id)
        if credential is None:
            raise ProvisioningCredentialNotFoundError("integration credential was not found")

        revoked_at = self._timestamp_mapper.to_datetime(self._clock.now_timestamp())
        revoked = self._transitioner.revoke(credential, revoked_at)
        await self._repository.update(revoked)
        return revoked
