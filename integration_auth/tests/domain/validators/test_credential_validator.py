"""Tests for integration credential snapshot validation."""

from datetime import UTC, datetime, timedelta

import pytest

from integration_auth.domain.enums.credential_status import CredentialStatus
from integration_auth.domain.validators.credential_validator import IntegrationCredentialValidator
from integration_auth.domain.validators.datetime_validator import AwareDateTimeValidator

ISSUED_AT = datetime(2026, 8, 22, 10, 0, tzinfo=UTC)


def build_validator() -> IntegrationCredentialValidator:
    return IntegrationCredentialValidator(AwareDateTimeValidator())


def test_accepts_active_credential_with_future_expiration() -> None:
    build_validator().validate(
        status=CredentialStatus.ACTIVE,
        issued_at=ISSUED_AT,
        expires_at=ISSUED_AT + timedelta(days=30),
        revoked_at=None,
    )


def test_accepts_revoked_credential_with_revocation_timestamp() -> None:
    build_validator().validate(
        status=CredentialStatus.REVOKED,
        issued_at=ISSUED_AT,
        expires_at=None,
        revoked_at=ISSUED_AT + timedelta(days=1),
    )


def test_accepts_expired_credential_with_expiration_timestamp() -> None:
    build_validator().validate(
        status=CredentialStatus.EXPIRED,
        issued_at=ISSUED_AT,
        expires_at=ISSUED_AT + timedelta(days=1),
        revoked_at=None,
    )


def test_rejects_expiration_not_later_than_issue_time() -> None:
    with pytest.raises(ValueError, match="expires_at must be later"):
        build_validator().validate(
            status=CredentialStatus.ACTIVE,
            issued_at=ISSUED_AT,
            expires_at=ISSUED_AT,
            revoked_at=None,
        )


def test_rejects_revocation_before_issue_time() -> None:
    with pytest.raises(ValueError, match="revoked_at must not be earlier"):
        build_validator().validate(
            status=CredentialStatus.REVOKED,
            issued_at=ISSUED_AT,
            expires_at=None,
            revoked_at=ISSUED_AT - timedelta(seconds=1),
        )


def test_rejects_active_credential_with_revocation_timestamp() -> None:
    with pytest.raises(ValueError, match="active credential"):
        build_validator().validate(
            status=CredentialStatus.ACTIVE,
            issued_at=ISSUED_AT,
            expires_at=None,
            revoked_at=ISSUED_AT,
        )


def test_rejects_revoked_credential_without_revocation_timestamp() -> None:
    with pytest.raises(ValueError, match="revoked credential"):
        build_validator().validate(
            status=CredentialStatus.REVOKED,
            issued_at=ISSUED_AT,
            expires_at=None,
            revoked_at=None,
        )


def test_rejects_expired_credential_without_expiration_timestamp() -> None:
    with pytest.raises(ValueError, match="expired credential requires"):
        build_validator().validate(
            status=CredentialStatus.EXPIRED,
            issued_at=ISSUED_AT,
            expires_at=None,
            revoked_at=None,
        )


def test_rejects_expired_credential_with_revocation_timestamp() -> None:
    with pytest.raises(ValueError, match="expired credential cannot"):
        build_validator().validate(
            status=CredentialStatus.EXPIRED,
            issued_at=ISSUED_AT,
            expires_at=ISSUED_AT + timedelta(days=1),
            revoked_at=ISSUED_AT,
        )


def test_rejects_naive_optional_datetime() -> None:
    naive_expiration = datetime(2026, 8, 23, 10, 0)

    with pytest.raises(ValueError, match="expires_at must be timezone-aware"):
        build_validator().validate(
            status=CredentialStatus.ACTIVE,
            issued_at=ISSUED_AT,
            expires_at=naive_expiration,
            revoked_at=None,
        )
