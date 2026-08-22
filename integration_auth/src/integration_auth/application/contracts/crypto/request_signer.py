"""Request signing contract."""

from typing import Protocol

from integration_auth.protocol.value_objects.canonical_request import CanonicalRequest


class RequestSigner(Protocol):
    """Sign a canonical integration request."""

    def sign(self, request: CanonicalRequest, secret: bytes) -> str: ...
