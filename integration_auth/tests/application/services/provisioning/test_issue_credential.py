"""Tests for credential issuance."""

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
from tests.support.application.provisioning.issue_credential_service_factory import (
    build_issue_credential_service,
)
from tests.support.application.provisioning.recording_secret_protector import (
    RecordingCredentialSecretProtector,
)

CLIENT_ID = IntegrationClientId("client-123")
NOW = 1787390042
RAW_SECRET = b"raw-secret"
PROTECTED_SECRET = b"protected-secret"


def test_issues_credential_and_persists_only_protected_secret() -> None:
    async def run() -> None:
        client_repository = IntegrationClientProvisioningRepositoryFake(
            (IntegrationClient(client_id=CLIENT_ID),)
        )
        credential_repository = IntegrationCredentialProvisioningRepositoryFake()
        protector = RecordingCredentialSecretProtector(PROTECTED_SECRET)
        service = build_issue_credential_service(
            client_repository=client_repository,
            credential_repository=credential_repository,
            protector=protector,
            timestamp=NOW,
            raw_secret=RAW_SECRET,
        )
        expires_at = datetime.fromtimestamp(NOW, tz=UTC) + timedelta(days=30)

        result = await service.issue(
            client_id=CLIENT_ID,
            direction=CredentialDirection.INBOUND,
            expires_at=expires_at,
        )

        assert result.raw_secret == RAW_SECRET
        assert "raw-secret" not in repr(result)
        assert result.credential.client_id == CLIENT_ID
        assert result.credential.direction is CredentialDirection.INBOUND
        assert result.credential.expires_at == expires_at
        assert protector.inputs == [RAW_SECRET]
        assert len(credential_repository.added) == 1
        stored_credential, stored_secret = credential_repository.added[0]
        assert stored_credential == result.credential
        assert isinstance(stored_secret, ProtectedCredentialSecret)
        assert stored_secret.value == PROTECTED_SECRET
        assert RAW_SECRET.decode() not in repr(stored_secret)

    asyncio.run(run())


def test_rejects_unknown_client_before_secret_protection_or_persistence() -> None:
    async def run() -> None:
        client_repository = IntegrationClientProvisioningRepositoryFake()
        credential_repository = IntegrationCredentialProvisioningRepositoryFake()
        protector = RecordingCredentialSecretProtector(PROTECTED_SECRET)
        service = build_issue_credential_service(
            client_repository=client_repository,
            credential_repository=credential_repository,
            protector=protector,
            timestamp=NOW,
            raw_secret=RAW_SECRET,
        )

        with pytest.raises(ProvisioningClientNotFoundError):
            await service.issue(
                client_id=CLIENT_ID,
                direction=CredentialDirection.OUTBOUND,
            )

        assert protector.inputs == []
        assert credential_repository.added == []

    asyncio.run(run())
