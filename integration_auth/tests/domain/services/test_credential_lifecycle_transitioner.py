"""Tests for credential lifecycle snapshot transitions."""

from datetime import UTC, datetime, timedelta

import pytest

from integration_auth.domain.enums.credential_status import CredentialStatus
from integration_auth.domain.services.credential_lifecycle_transitioner import (
    CredentialLifecycleTransitioner,
)
from tests.support.application.provisioning.lifecycle_transitioner_factory import (
    build_credential_lifecycle_transitioner,
)
from tests.support.domain.integration_credential_builder import IntegrationCredentialBuilder


def test_revoke_builds_valid_revoked_snapshot() -> None:
    credential = IntegrationCredentialBuilder().build()
    revoked_at = credential.issued_at + timedelta(minutes=1)

    result = build_credential_lifecycle_transitioner().revoke(
        credential,
        revoked_at,
    )

    assert result.status is CredentialStatus.REVOKED
    assert result.revoked_at == revoked_at


def test_expire_builds_valid_expired_snapshot() -> None:
    credential = IntegrationCredentialBuilder().build()
    expires_at = credential.issued_at + timedelta(minutes=1)

    result = build_credential_lifecycle_transitioner().expire(
        credential,
        expires_at,
    )

    assert result.status is CredentialStatus.EXPIRED
    assert result.expires_at == expires_at
    assert result.revoked_at is None


def test_terminal_credential_cannot_transition_again() -> None:
    builder = IntegrationCredentialBuilder()
    builder.status = CredentialStatus.REVOKED
    builder.revoked_at = datetime(2026, 8, 22, 10, 1, tzinfo=UTC)
    credential = builder.build()

    with pytest.raises(ValueError, match="cannot transition"):
        build_credential_lifecycle_transitioner().expire(
            credential,
            datetime(2026, 8, 22, 10, 2, tzinfo=UTC),
        )


def test_transitioner_is_a_focused_domain_service() -> None:
    transitioner = build_credential_lifecycle_transitioner()

    assert isinstance(transitioner, CredentialLifecycleTransitioner)
