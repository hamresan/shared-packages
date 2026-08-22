"""Issue integration credentials."""

from datetime import datetime

from integration_auth.application.contracts.authentication.clock import Clock
from integration_auth.application.contracts.provisioning.id_generators import (
    IntegrationCredentialIdGenerator,
)
from integration_auth.application.contracts.provisioning.repositories import (
    IntegrationClientProvisioningRepository,
    IntegrationCredentialProvisioningRepository,
)
from integration_auth.application.contracts.provisioning.secrets import (
    CredentialSecretGenerator,
    CredentialSecretProtector,
)
from integration_auth.application.dto.provisioning.issued_credential import IssuedCredential
from integration_auth.application.errors.provisioning import ProvisioningClientNotFoundError
from integration_auth.application.mappers.time import UnixTimestampMapper
from integration_auth.domain.entities.integration_credential import IntegrationCredential
from integration_auth.domain.enums.credential_direction import CredentialDirection
from integration_auth.domain.enums.credential_status import CredentialStatus
from integration_auth.domain.value_objects.identifiers import IntegrationClientId


class IssueCredentialService:
    """Issue a credential and persist only protected secret material."""

    def __init__(
        self,
        *,
        client_repository: IntegrationClientProvisioningRepository,
        credential_repository: IntegrationCredentialProvisioningRepository,
        credential_id_generator: IntegrationCredentialIdGenerator,
        secret_generator: CredentialSecretGenerator,
        secret_protector: CredentialSecretProtector,
        clock: Clock,
        timestamp_mapper: UnixTimestampMapper,
    ) -> None:
        self._client_repository = client_repository
        self._credential_repository = credential_repository
        self._credential_id_generator = credential_id_generator
        self._secret_generator = secret_generator
        self._secret_protector = secret_protector
        self._clock = clock
        self._timestamp_mapper = timestamp_mapper

    async def issue(
        self,
        *,
        client_id: IntegrationClientId,
        direction: CredentialDirection,
        expires_at: datetime | None = None,
    ) -> IssuedCredential:
        client = await self._client_repository.get_by_id(client_id)
        if client is None:
            raise ProvisioningClientNotFoundError("integration client was not found")

        issued_at = self._timestamp_mapper.to_datetime(self._clock.now_timestamp())
        credential = IntegrationCredential(
            credential_id=self._credential_id_generator.generate(),
            client_id=client_id,
            direction=direction,
            status=CredentialStatus.ACTIVE,
            issued_at=issued_at,
            expires_at=expires_at,
        )
        raw_secret = self._secret_generator.generate()
        protected_secret = self._secret_protector.protect(raw_secret)
        await self._credential_repository.add(credential, protected_secret)
        return IssuedCredential(credential=credential, raw_secret=raw_secret)
