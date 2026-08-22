"""Parse signed integration request headers."""

from fastapi import Request

from integration_auth.presentation.schemas.signed_request_headers import SignedRequestHeaders

CLIENT_ID_HEADER = "X-Integration-Client-Id"
TIMESTAMP_HEADER = "X-Integration-Timestamp"
NONCE_HEADER = "X-Integration-Nonce"
SIGNATURE_HEADER = "X-Integration-Signature"


class InvalidSignedRequestHeadersError(ValueError):
    """Raised when required integration authentication headers are missing or invalid."""


class SignedRequestHeaderParser:
    """Validate and normalize signed-request authentication headers."""

    def parse(self, request: Request) -> SignedRequestHeaders:
        client_id = self._required(request, CLIENT_ID_HEADER)
        timestamp_value = self._required(request, TIMESTAMP_HEADER)
        nonce = self._required(request, NONCE_HEADER)
        signature = self._required(request, SIGNATURE_HEADER)
        try:
            timestamp = int(timestamp_value)
        except ValueError as exc:
            raise InvalidSignedRequestHeadersError("invalid integration timestamp") from exc
        return SignedRequestHeaders(
            client_id=client_id,
            timestamp=timestamp,
            nonce=nonce,
            signature=signature,
        )

    @staticmethod
    def _required(request: Request, name: str) -> str:
        value = request.headers.get(name)
        if value is None or not value.strip():
            raise InvalidSignedRequestHeadersError("missing integration authentication header")
        return value.strip()
