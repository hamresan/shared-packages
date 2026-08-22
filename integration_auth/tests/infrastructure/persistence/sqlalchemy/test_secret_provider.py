"""Tests for the SQLAlchemy credential secret provider."""

import asyncio
from pathlib import Path

from integration_auth.application.security.protected_credential_secret import (
    ProtectedCredentialSecret,
)
from integration_auth.domain.value_objects.identifiers import IntegrationCredentialId
from integration_auth.infrastructure.persistence.sqlalchemy.mappers.credential_mapper import (
    IntegrationCredentialRecordMapper,
)
from integration_auth.infrastructure.persistence.sqlalchemy.repositories.credential_repository import (
    SqlAlchemyIntegrationCredentialRepository,
)
from integration_auth.infrastructure.persistence.sqlalchemy.repositories.secret_provider import (
    SqlAlchemyCredentialSecretProvider,
)
from tests.support.infrastructure.persistence.sqlalchemy.credential_factory import (
    build_persistence_credential,
)
from tests.support.infrastructure.persistence.sqlalchemy.database import SqlAlchemyTestDatabase
from tests.support.infrastructure.persistence.sqlalchemy.secret_unprotector import (
    PrefixCredentialSecretUnprotector,
)


def test_secret_provider_recovers_only_transient_verification_material(tmp_path: Path) -> None:
    async def run() -> None:
        database = SqlAlchemyTestDatabase(tmp_path / "secrets.db")
        await database.create_schema()
        credential = build_persistence_credential("credential-secret")
        repository = SqlAlchemyIntegrationCredentialRepository(
            database.session_factory,
            IntegrationCredentialRecordMapper(),
        )
        await repository.add(
            credential,
            ProtectedCredentialSecret(b"protected:raw-secret"),
        )
        provider = SqlAlchemyCredentialSecretProvider(
            database.session_factory,
            PrefixCredentialSecretUnprotector(),
        )

        assert await provider.get_verification_secret(credential.credential_id) == b"raw-secret"
        assert (
            await provider.get_verification_secret(IntegrationCredentialId("missing-credential"))
            is None
        )
        await database.dispose()

    asyncio.run(run())
