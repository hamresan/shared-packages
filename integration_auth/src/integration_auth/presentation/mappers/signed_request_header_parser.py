"""Parse signed integration request headers."""

from fastapi import Request

from integration_auth.presentation.schemas.signed_request_headers import SignedRequestHeaders
from integration_auth.presentation.validators.required_header_reader import (
    InvalidSignedRequestHeadersError,
    RequiredHeaderReader,
)

CLIENT_ID_HEADER = "X-Integration-Client-Id"
TIMESTAMP_HEADER = "X-Integration-Timestamp"
NONCE_HEADER = "X-Integration-Nonce"
SIGNATURE_HEADER = "X-Integration-Signature"


class SignedRequestHeaderParser:
    """Validate and normalize signed-request authentication headers."""

    def __init__(self, header_reader: RequiredHeaderReader) -> None:
        self._header_reader = header_reader

    def parse(self, request: Request) -> SignedRequestHeaders:
        client_id = self._header_reader.read(request, CLIENT_ID_HEADER)
        timestamp_value = self._header_reader.read(request, TIMESTAMP_HEADER)
        nonce = self._header_reader.read(request, NONCE_HEADER)
        signature = self._header_reader.read(request, SIGNATURE_HEADER)
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
