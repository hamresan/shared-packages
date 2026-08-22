"""Request signature verification contract."""

from typing import Protocol

from integration_auth.protocol.value_objects.canonical_request import CanonicalRequest


class RequestVerifier(Protocol):
    """Verify a canonical integration request signature."""

    def verify(self, request: CanonicalRequest, secret: bytes, signature: str) -> bool: ...
