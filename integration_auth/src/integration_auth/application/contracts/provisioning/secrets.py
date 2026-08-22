"""Credential secret generation, protection, and recovery contracts."""

from typing import Protocol

from integration_auth.application.security.protected_credential_secret import (
    ProtectedCredentialSecret,
)


class CredentialSecretGenerator(Protocol):
    """Generate cryptographically strong raw credential secrets."""

    def generate(self) -> bytes: ...


class CredentialSecretProtector(Protocol):
    """Protect raw secret material before persistence."""

    def protect(self, secret: bytes) -> ProtectedCredentialSecret: ...


class CredentialSecretUnprotector(Protocol):
    """Recover transient verification material from protected persistence data."""

    def unprotect(self, secret: ProtectedCredentialSecret) -> bytes: ...
