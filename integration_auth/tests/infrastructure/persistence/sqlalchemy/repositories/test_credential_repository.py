"""Tests for the SQLAlchemy integration-credential repository."""

import asyncio
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

import pytest

from integration_auth.application.security.protected_credential_secret import (
    ProtectedCredentialSecret,
)
from integration_auth.domain.enums.credential_status import CredentialStatus
from integration_auth.infrastructure.persistence.sqlalchemy.mappers.credential_mapper import (
    IntegrationCredentialRecordMapper,
)
from integration_auth.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemyIntegrationCredentialRepository,
)
from tests.support.infrastructure.persistence.sqlalchemy.credential_factory import (
    PERSISTENCE_TEST_CLIENT_ID,
    PERSISTENCE_TEST_ISSUED_AT,
    build_persistence_credential,
)
from tests.support.infrastructure.persistence.sqlalchemy.database import SqlAlchemyTestDatabase


def test_credential_repository_round_trips_metadata_and_protected_secret(tmp_path: Path) -> None:
    async def run() -> None:
        database = SqlAlchemyTestDatabase(tmp_path / "credentials.db")
        await database.create_schema()
        repository = SqlAlchemyIntegrationCredentialRepository(
            database.session_factory,
            IntegrationCredentialRecordMapper(),
        )
        credential = build_persistence_credential("credential-1")
        await repository.add(credential, ProtectedCredentialSecret(b"protected:secret"))
        assert await repository.get_by_id(credential.credential_id) == credential
        assert await repository.list_for_client(PERSISTENCE_TEST_CLIENT_ID) == (credential,)

        revoked = replace(
            credential,
            status=CredentialStatus.REVOKED,
            revoked_at=PERSISTENCE_TEST_ISSUED_AT + timedelta(minutes=1),
        )
        await repository.update(revoked)
        assert await repository.get_by_id(credential.credential_id) == revoked
        await database.dispose()

    asyncio.run(run())


def test_rotation_is_atomic_when_a_previous_credential_is_missing(tmp_path: Path) -> None:
    async def run() -> None:
        database = SqlAlchemyTestDatabase(tmp_path / "rotation.db")
        await database.create_schema()
        repository = SqlAlchemyIntegrationCredentialRepository(
            database.session_factory,
            IntegrationCredentialRecordMapper(),
        )
        existing = build_persistence_credential("existing")
        await repository.add(existing, ProtectedCredentialSecret(b"protected:old"))
        shortened = replace(
            existing,
            expires_at=PERSISTENCE_TEST_ISSUED_AT + timedelta(minutes=5),
        )
        missing = build_persistence_credential("missing")
        replacement = build_persistence_credential("replacement")

        with pytest.raises(LookupError):
            await repository.rotate(
                previous_credentials=(shortened, missing),
                new_credential=replacement,
                protected_secret=ProtectedCredentialSecret(b"protected:new"),
            )

        assert await repository.get_by_id(existing.credential_id) == existing
        assert await repository.get_by_id(replacement.credential_id) is None
        await database.dispose()

    asyncio.run(run())
