"""Cryptographically strong OAuth state generation."""

import secrets

from instagram_auth.application.contracts import StateGenerator


class SecretsStateGenerator(StateGenerator):
    """Generate URL-safe OAuth state using Python's cryptographic RNG."""

    def __init__(self, *, entropy_bytes: int = 32) -> None:
        if entropy_bytes < 32:
            raise ValueError("OAuth state requires at least 32 bytes of entropy")
        self._entropy_bytes = entropy_bytes

    def generate(self) -> str:
        """Return a cryptographically strong URL-safe state value."""
        return secrets.token_urlsafe(self._entropy_bytes)
