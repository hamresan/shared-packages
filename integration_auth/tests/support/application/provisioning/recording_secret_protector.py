"""Recording credential secret protector for tests."""

from integration_auth.application.contracts.provisioning.secrets import CredentialSecretProtector
from integration_auth.application.security.protected_credential_secret import (
    ProtectedCredentialSecret,
)


class RecordingCredentialSecretProtector(CredentialSecretProtector):
    """Record raw input and return deterministic protected material."""

    def __init__(self, protected_secret: bytes = b"protected-stage-6-secret") -> None:
        self._protected_secret = ProtectedCredentialSecret(protected_secret)
        self.inputs: list[bytes] = []

    def protect(self, secret: bytes) -> ProtectedCredentialSecret:
        self.inputs.append(secret)
        return self._protected_secret
