"""Tests for IssuedCredential."""

from integration_auth.application.dto.provisioning.issued_credential import IssuedCredential
from tests.support.domain.integration_credential_builder import IntegrationCredentialBuilder


def test_hides_raw_secret_from_repr() -> None:
    result = IssuedCredential(
        credential=IntegrationCredentialBuilder().build(),
        raw_secret=b"raw-secret-value",
    )

    assert result.raw_secret == b"raw-secret-value"
    assert "raw-secret-value" not in repr(result)
