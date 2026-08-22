"""Tests for credential revoke and expire services."""

import asyncio
from datetime import UTC, datetime, timedelta

import pytest

from integration_auth.application.errors.provisioning import ProvisioningCredentialNotFoundError
from integration_auth.application.mappers.time import UnixTimestampMapper
from integration_auth.application.services.provisioning.expire_credential import (
    ExpireCredentialService,
)
from integration_auth.application.services.provisioning.revoke_credential import (
    RevokeCredentialService,
)
from integration_auth.domain.enums.credential_status import CredentialStatus
from integration_auth.domain.value_objects.identifiers import IntegrationCredentialId
from tests.support.application.authentication.fixed_clock import FixedClock
from tests.support.application.provisioning.integration_credential_repository_fake import (
    IntegrationCredentialProvisioningRepositoryFake,
)
from tests.support.application.provisioning.lifecycle_transitioner_factory import (
    build_credential_lifecycle_transitioner,
)
from tests.support.domain.integration_credential_builder import IntegrationCredentialBuilder

NOW = 1787390042


def test_revoke_updates_credential_snapshot() -> None:
    async def run() -> None:
        builder = IntegrationCredentialBuilder()
        builder.issued_at = datetime.fromtimestamp(NOW, tz=UTC) - timedelta(minutes=1)
        credential = builder.build()
        repository = IntegrationCredentialProvisioningRepositoryFake((credential,))
        service = RevokeCredentialService(
            repository=repository,
            transitioner=build_credential_lifecycle_transitioner(),
            clock=FixedClock(NOW),
            timestamp_mapper=UnixTimestampMapper(),
        )

        result = await service.revoke(credential.credential_id)

        assert result.status is CredentialStatus.REVOKED
        assert result.revoked_at == datetime.fromtimestamp(NOW, tz=UTC)
        assert repository.updated == [result]

    asyncio.run(run())


def test_expire_updates_credential_snapshot() -> None:
    async def run() -> None:
        builder = IntegrationCredentialBuilder()
        builder.issued_at = datetime.fromtimestamp(NOW, tz=UTC) - timedelta(minutes=1)
        credential = builder.build()
        repository = IntegrationCredentialProvisioningRepositoryFake((credential,))
        service = ExpireCredentialService(
            repository=repository,
            transitioner=build_credential_lifecycle_transitioner(),
            clock=FixedClock(NOW),
            timestamp_mapper=UnixTimestampMapper(),
        )

        result = await service.expire(credential.credential_id)

        assert result.status is CredentialStatus.EXPIRED
        assert result.expires_at == datetime.fromtimestamp(NOW, tz=UTC)
        assert repository.updated == [result]

    asyncio.run(run())


def test_revoke_missing_credential_fails_closed() -> None:
    async def run() -> None:
        repository = IntegrationCredentialProvisioningRepositoryFake()
        service = RevokeCredentialService(
            repository=repository,
            transitioner=build_credential_lifecycle_transitioner(),
            clock=FixedClock(NOW),
            timestamp_mapper=UnixTimestampMapper(),
        )

        with pytest.raises(ProvisioningCredentialNotFoundError):
            await service.revoke(IntegrationCredentialId("missing"))

        assert repository.updated == []

    asyncio.run(run())


def test_expire_missing_credential_fails_closed() -> None:
    async def run() -> None:
        repository = IntegrationCredentialProvisioningRepositoryFake()
        service = ExpireCredentialService(
            repository=repository,
            transitioner=build_credential_lifecycle_transitioner(),
            clock=FixedClock(NOW),
            timestamp_mapper=UnixTimestampMapper(),
        )

        with pytest.raises(ProvisioningCredentialNotFoundError):
            await service.expire(IntegrationCredentialId("missing"))

        assert repository.updated == []

    asyncio.run(run())
