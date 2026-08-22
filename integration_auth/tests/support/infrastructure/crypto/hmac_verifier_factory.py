"""Factory for HMAC request verifier tests."""

from integration_auth.application.contracts.crypto.request_verifier import RequestVerifier
from integration_auth.infrastructure.crypto.hmac.hmac_sha256_request_signer import (
    HmacSha256RequestSigner,
)
from integration_auth.infrastructure.crypto.hmac.hmac_sha256_request_verifier import (
    HmacSha256RequestVerifier,
)
from integration_auth.protocol.canonicalization.canonical_request_serializer import (
    CanonicalRequestSerializer,
)


class HmacVerifierFactory:
    """Build a verifier with the production HMAC signer composition."""

    def build(self) -> RequestVerifier:
        signer = HmacSha256RequestSigner(CanonicalRequestSerializer())
        return HmacSha256RequestVerifier(signer)
