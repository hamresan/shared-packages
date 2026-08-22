"""Deterministic secret unprotector for SQLAlchemy adapter tests."""

from integration_auth.application.contracts.provisioning.secrets import CredentialSecretUnprotector
from integration_auth.application.security.protected_credential_secret import (
    ProtectedCredentialSecret,
)


class PrefixCredentialSecretUnprotector(CredentialSecretUnprotector):
    """Recover test secrets from a deterministic prefix-protected representation."""

    def unprotect(self, secret: ProtectedCredentialSecret) -> bytes:
        prefix = b"protected:"
        if not secret.value.startswith(prefix):
            raise ValueError("unexpected protected test secret")
        return secret.value[len(prefix) :]
