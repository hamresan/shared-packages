"""Tests for IntegrationCredential."""

from datetime import timedelta

import pytest

from integration_auth.domain.enums.credential_direction import CredentialDirection
from integration_auth.domain.enums.credential_status import CredentialStatus
from tests.support.domain.integration_credential_builder import IntegrationCredentialBuilder


def test_credential_contains_no_secret_material_and_preserves_metadata() -> None:
    credential = IntegrationCredentialBuilder().build()

    assert credential.direction is CredentialDirection.INBOUND
    assert credential.status is CredentialStatus.ACTIVE
    assert not hasattr(credential, "secret")


def test_credential_enforces_lifecycle_snapshot_invariants() -> None:
    builder = IntegrationCredentialBuilder()
    builder.status = CredentialStatus.REVOKED

    with pytest.raises(ValueError, match="revoked credential requires"):
        builder.build()


def test_expired_credential_requires_valid_expiration() -> None:
    builder = IntegrationCredentialBuilder()
    builder.status = CredentialStatus.EXPIRED
    builder.expires_at = builder.issued_at + timedelta(days=30)

    credential = builder.build()

    assert credential.status is CredentialStatus.EXPIRED
    assert credential.expires_at == builder.expires_at
