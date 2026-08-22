"""HMAC-SHA256 canonical request signing."""

import hashlib
import hmac

from integration_auth.application.contracts.crypto.request_signer import RequestSigner
from integration_auth.protocol.canonicalization.canonical_request_serializer import (
    CanonicalRequestSerializer,
)
from integration_auth.protocol.value_objects.canonical_request import CanonicalRequest


class HmacSha256RequestSigner(RequestSigner):
    """Sign canonical requests using HMAC-SHA256 and lowercase hex encoding."""

    def __init__(self, serializer: CanonicalRequestSerializer) -> None:
        self._serializer = serializer

    def sign(self, request: CanonicalRequest, secret: bytes) -> str:
        if not secret:
            raise ValueError("HMAC secret must not be empty")
        message = self._serializer.serialize(request).encode("utf-8")
        return hmac.new(secret, message, hashlib.sha256).hexdigest()
