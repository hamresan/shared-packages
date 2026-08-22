"""Tests for signed integration request header parsing."""

import pytest

from integration_auth.presentation.mappers.signed_request_header_parser import SignedRequestHeaderParser
from integration_auth.presentation.validators.required_header_reader import (
    InvalidSignedRequestHeadersError,
    RequiredHeaderReader,
)
from tests.support.presentation.request_builder import FastApiRequestBuilder
from tests.support.presentation.signed_headers import SIGNED_HEADERS


def test_signed_request_header_parser_maps_all_values() -> None:
    request = FastApiRequestBuilder().build(headers=SIGNED_HEADERS)

    parsed = SignedRequestHeaderParser(RequiredHeaderReader()).parse(request)

    assert parsed.client_id == "client-123"
    assert parsed.timestamp == 1_787_418_000
    assert parsed.nonce == "nonce-123"
    assert parsed.signature == "signature-123"


def test_signed_request_header_parser_rejects_non_integer_timestamp() -> None:
    headers = dict(SIGNED_HEADERS)
    headers["X-Integration-Timestamp"] = "invalid"
    request = FastApiRequestBuilder().build(headers=headers)

    with pytest.raises(InvalidSignedRequestHeadersError, match="invalid integration timestamp"):
        SignedRequestHeaderParser(RequiredHeaderReader()).parse(request)
