"""Tests for ProtectedCredentialSecret."""

import pytest

from integration_auth.application.security.protected_credential_secret import (
    ProtectedCredentialSecret,
)


def test_hides_protected_material_from_repr() -> None:
    secret = ProtectedCredentialSecret(b"encrypted-material")

    assert secret.value == b"encrypted-material"
    assert "encrypted-material" not in repr(secret)


def test_rejects_empty_protected_material() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        ProtectedCredentialSecret(b"")
