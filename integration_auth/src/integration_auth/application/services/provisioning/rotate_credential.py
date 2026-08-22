"""Rotate integration credentials."""

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
from integration_auth.domain.policies.credential_rotation_policy import CredentialRotationPolicy
from integration_auth.domain.value_objects.identifiers import IntegrationClientId


class RotateCredentialService:
    """Issue a replacement credential with an explicit overlap window."""

    def __init__(
        self,
        *,
        client_repository: IntegrationClientProvisioningRepository,
        credential_repository: IntegrationCredentialProvisioningRepository,
        credential_id_generator: IntegrationCredentialIdGenerator,
        secret_generator: CredentialSecretGenerator,
        secret_protector: CredentialSecretProtector,
        rotation_policy: CredentialRotationPolicy,
        clock: Clock,
        timestamp_mapper: UnixTimestampMapper,
    ) -> None:
        self._client_repository = client_repository
        self._credential_repository = credential_repository
        self._credential_id_generator = credential_id_generator
        self._secret_generator = secret_generator
        self._secret_protector = secret_protector
        self._rotation_policy = rotation_policy
        self._clock = clock
        self._timestamp_mapper = timestamp_mapper

    async def rotate(
        self,
        *,
        client_id: IntegrationClientId,
        direction: CredentialDirection,
        overlap_seconds: int,
        expires_at: datetime | None = None,
    ) -> IssuedCredential:
        client = await self._client_repository.get_by_id(client_id)
        if client is None:
            raise ProvisioningClientNotFoundError("integration client was not found")

        current_timestamp = self._clock.now_timestamp()
        credentials = await self._credential_repository.list_for_client(client_id)
        previous_credentials = self._rotation_policy.prepare_previous_credentials(
            credentials=credentials,
            client_id=client_id,
            direction=direction,
            current_timestamp=current_timestamp,
            overlap_seconds=overlap_seconds,
        )
        issued_at = self._timestamp_mapper.to_datetime(current_timestamp)
        new_credential = IntegrationCredential(
            credential_id=self._credential_id_generator.generate(),
            client_id=client_id,
            direction=direction,
            status=CredentialStatus.ACTIVE,
            issued_at=issued_at,
            expires_at=expires_at,
        )
        raw_secret = self._secret_generator.generate()
        protected_secret = self._secret_protector.protect(raw_secret)
        await self._credential_repository.rotate(
            previous_credentials=previous_credentials,
            new_credential=new_credential,
            protected_secret=protected_secret,
        )
        return IssuedCredential(credential=new_credential, raw_secret=raw_secret)
