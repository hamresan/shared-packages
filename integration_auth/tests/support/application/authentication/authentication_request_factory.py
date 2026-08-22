"""Factory for signed authentication-request test DTOs."""

from integration_auth.application.dto.authentication.authenticate_integration_request import (
    AuthenticateIntegrationRequest,
)
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.infrastructure.crypto.hmac.hmac_sha256_request_signer import (
    HmacSha256RequestSigner,
)
from integration_auth.protocol.canonicalization.canonical_request_serializer import (
    CanonicalRequestSerializer,
)
from integration_auth.protocol.value_objects.canonical_request import CanonicalRequest


def build_signed_authentication_request(
    *,
    client_id: IntegrationClientId,
    request: CanonicalRequest,
    secret: bytes,
) -> AuthenticateIntegrationRequest:
    """Build an authentication DTO signed with the real Stage 2 HMAC implementation."""
    signer = HmacSha256RequestSigner(CanonicalRequestSerializer())
    return AuthenticateIntegrationRequest(
        client_id=client_id,
        request=request,
        signature=signer.sign(request, secret),
    )
