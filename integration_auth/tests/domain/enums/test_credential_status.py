"""Tests for CredentialStatus."""

from integration_auth.domain.enums import CredentialStatus


def test_credential_status_values_are_stable_external_strings() -> None:
    assert CredentialStatus.ACTIVE.value == "active"
    assert CredentialStatus.REVOKED.value == "revoked"
    assert CredentialStatus.EXPIRED.value == "expired"
