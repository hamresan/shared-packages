"""Body hashing contract."""

from typing import Protocol


class BodyHasher(Protocol):
    """Hash a request body for inclusion in a canonical request."""

    def hash(self, body: bytes) -> str: ...
