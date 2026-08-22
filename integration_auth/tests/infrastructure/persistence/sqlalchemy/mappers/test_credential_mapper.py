"""Tests for integration-credential persistence mapping."""

from dataclasses import replace
from datetime import timedelta

from integration_auth.application.security.protected_credential_secret import (
    ProtectedCredentialSecret,
)
from integration_auth.infrastructure.persistence.sqlalchemy.mappers.credential_mapper import (
    IntegrationCredentialRecordMapper,
)
from tests.support.infrastructure.persistence.sqlalchemy.credential_factory import (
    PERSISTENCE_TEST_ISSUED_AT,
    build_persistence_credential,
)


def test_credential_mapper_keeps_secret_out_of_domain_and_updates_metadata() -> None:
    mapper = IntegrationCredentialRecordMapper()
    credential = build_persistence_credential("credential-123")
    protected = ProtectedCredentialSecret(b"protected:secret")
    record = mapper.to_record(credential, protected)

    assert record.protected_secret == protected.value
    assert mapper.to_domain(record) == credential

    expiring = replace(
        credential,
        expires_at=PERSISTENCE_TEST_ISSUED_AT + timedelta(minutes=5),
    )
    mapper.apply_metadata(record, expiring)
    assert mapper.to_domain(record) == expiring
    assert record.protected_secret == protected.value
