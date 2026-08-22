"""Tests for credential rotation."""

import asyncio
from datetime import UTC, datetime, timedelta

import pytest

from integration_auth.application.errors.provisioning import ProvisioningClientNotFoundError
from integration_auth.application.security.protected_credential_secret import (
    ProtectedCredentialSecret,
)
from integration_auth.domain.entities.integration_client import IntegrationClient
from integration_auth.domain.enums.credential_direction import CredentialDirection
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from tests.support.application.provisioning.integration_client_repository_fake import (
    IntegrationClientProvisioningRepositoryFake,
)
from tests.support.application.provisioning.integration_credential_repository_fake import (
    IntegrationCredentialProvisioningRepositoryFake,
)
from tests.support.application.provisioning.recording_secret_protector import (
    RecordingCredentialSecretProtector,
)
from tests.support.application.provisioning.rotate_credential_service_factory import (
    build_rotate_credential_service,
)
from tests.support.application.provisioning.rotation_credential_builder import (
    RotationCredentialBuilder,
)

CLIENT_ID = IntegrationClientId("client-123")
NOW = 1787390042
RAW_SECRET = b"rotation-raw-secret"
PROTECTED_SECRET = b"rotation-protected-secret"


def test_rotates_same_direction_credentials_with_explicit_overlap() -> None:
    async def run() -> None:
        previous = RotationCredentialBuilder(
            current_timestamp=NOW,
            client_id=CLIENT_ID,
        ).build()
        outbound = (
            RotationCredentialBuilder(
                current_timestamp=NOW,
                client_id=CLIENT_ID,
            )
            .with_direction(CredentialDirection.OUTBOUND)
            .build()
        )
        client_repository = IntegrationClientProvisioningRepositoryFake(
            (IntegrationClient(client_id=CLIENT_ID),)
        )
        credential_repository = IntegrationCredentialProvisioningRepositoryFake(
            (previous, outbound)
        )
        protector = RecordingCredentialSecretProtector(PROTECTED_SECRET)
        service = build_rotate_credential_service(
            client_repository=client_repository,
            credential_repository=credential_repository,
            protector=protector,
            timestamp=NOW,
            raw_secret=RAW_SECRET,
        )

        result = await service.rotate(
            client_id=CLIENT_ID,
            direction=CredentialDirection.INBOUND,
            overlap_seconds=120,
        )

        assert result.raw_secret == RAW_SECRET
        assert result.credential.direction is CredentialDirection.INBOUND
        assert len(credential_repository.rotations) == 1
        previous_updates, new_credential, protected = credential_repository.rotations[0]
        assert previous_updates[0].credential_id == previous.credential_id
        assert previous_updates[0].expires_at == datetime.fromtimestamp(
            NOW,
            tz=UTC,
        ) + timedelta(seconds=120)
        assert all(item.credential_id != outbound.credential_id for item in previous_updates)
        assert new_credential == result.credential
        assert isinstance(protected, ProtectedCredentialSecret)
        assert protected.value == PROTECTED_SECRET
        assert RAW_SECRET.decode() not in repr(protected)

    asyncio.run(run())


def test_rotation_fails_closed_for_unknown_client() -> None:
    async def run() -> None:
        credential_repository = IntegrationCredentialProvisioningRepositoryFake()
        protector = RecordingCredentialSecretProtector(PROTECTED_SECRET)
        service = build_rotate_credential_service(
            client_repository=IntegrationClientProvisioningRepositoryFake(),
            credential_repository=credential_repository,
            protector=protector,
            timestamp=NOW,
            raw_secret=RAW_SECRET,
        )

        with pytest.raises(ProvisioningClientNotFoundError):
            await service.rotate(
                client_id=CLIENT_ID,
                direction=CredentialDirection.INBOUND,
                overlap_seconds=0,
            )

        assert credential_repository.rotations == []
        assert protector.inputs == []

    asyncio.run(run())
