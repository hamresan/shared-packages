"""Map FastAPI requests to application authentication inputs."""

from fastapi import Request

from integration_auth.application.contracts.crypto.body_hasher import BodyHasher
from integration_auth.application.dto.authentication import AuthenticateIntegrationRequest
from integration_auth.domain.value_objects.identifiers import IntegrationClientId
from integration_auth.presentation.schemas.signed_request_headers import SignedRequestHeaders
from integration_auth.protocol.canonicalization.canonical_query import CanonicalQueryEncoder
from integration_auth.protocol.value_objects.canonical_request import CanonicalRequest


class FastApiAuthenticationRequestMapper:
    """Translate HTTP request data without leaking FastAPI into the application layer."""

    def __init__(self, *, body_hasher: BodyHasher, query_encoder: CanonicalQueryEncoder) -> None:
        self._body_hasher = body_hasher
        self._query_encoder = query_encoder

    async def map(
        self,
        request: Request,
        headers: SignedRequestHeaders,
    ) -> AuthenticateIntegrationRequest:
        body = await request.body()
        canonical_request = CanonicalRequest(
            method=request.method,
            path=request.url.path,
            canonical_query=self._query_encoder.encode(request.query_params.multi_items()),
            timestamp=headers.timestamp,
            nonce=headers.nonce,
            body_sha256=self._body_hasher.hash(body),
        )
        return AuthenticateIntegrationRequest(
            client_id=IntegrationClientId(headers.client_id),
            request=canonical_request,
            signature=headers.signature,
        )
