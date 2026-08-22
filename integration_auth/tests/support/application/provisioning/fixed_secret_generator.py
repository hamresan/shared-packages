"""Deterministic credential secret generator for tests."""

from integration_auth.application.contracts.provisioning.secrets import CredentialSecretGenerator


class FixedCredentialSecretGenerator(CredentialSecretGenerator):
    """Return one configured raw secret."""

    def __init__(self, secret: bytes = b"raw-stage-6-secret") -> None:
        self._secret = secret

    def generate(self) -> bytes:
        return self._secret
