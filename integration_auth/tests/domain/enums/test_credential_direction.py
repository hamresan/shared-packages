"""Tests for CredentialDirection."""

from integration_auth.domain.enums import CredentialDirection


def test_credential_direction_values_are_stable_external_strings() -> None:
    assert CredentialDirection.INBOUND.value == "inbound"
    assert CredentialDirection.OUTBOUND.value == "outbound"
