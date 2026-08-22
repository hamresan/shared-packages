"""Expire integration credentials."""

from integration_auth.application.contracts.authentication.clock import Clock
from integration_auth.application.contracts.provisioning.repositories import (
    IntegrationCredentialProvisioningRepository,
)
from integration_auth.application.errors.provisioning import ProvisioningCredentialNotFoundError
from integration_auth.application.mappers.time import UnixTimestampMapper
from integration_auth.domain.entities.integration_credential import IntegrationCredential
from integration_auth.domain.services.credential_lifecycle_transitioner import (
    CredentialLifecycleTransitioner,
)
from integration_auth.domain.value_objects.identifiers import IntegrationCredentialId


class ExpireCredentialService:
    """Expire one credential through the lifecycle transition boundary."""

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

    async def expire(self, credential_id: IntegrationCredentialId) -> IntegrationCredential:
        credential = await self._repository.get_by_id(credential_id)
        if credential is None:
            raise ProvisioningCredentialNotFoundError("integration credential was not found")

        expires_at = self._timestamp_mapper.to_datetime(self._clock.now_timestamp())
        expired = self._transitioner.expire(credential, expires_at)
        await self._repository.update(expired)
        return expired
