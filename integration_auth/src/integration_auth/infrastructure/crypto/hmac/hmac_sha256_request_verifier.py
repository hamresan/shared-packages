"""HMAC-SHA256 canonical request verification."""

import hmac

from integration_auth.application.contracts.crypto.request_signer import RequestSigner
from integration_auth.application.contracts.crypto.request_verifier import RequestVerifier
from integration_auth.protocol.value_objects.canonical_request import CanonicalRequest


class HmacSha256RequestVerifier(RequestVerifier):
    """Verify request signatures with constant-time comparison."""

    def __init__(self, signer: RequestSigner) -> None:
        self._signer = signer

    def verify(self, request: CanonicalRequest, secret: bytes, signature: str) -> bool:
        expected_signature = self._signer.sign(request, secret)
        return hmac.compare_digest(expected_signature, signature)
