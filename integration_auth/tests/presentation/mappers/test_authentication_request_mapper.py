"""Tests for FastAPI request to authentication DTO mapping."""

import asyncio

from integration_auth.infrastructure.crypto.hashing.sha256_body_hasher import Sha256BodyHasher
from integration_auth.presentation.mappers.authentication_request_mapper import (
    FastApiAuthenticationRequestMapper,
)
from integration_auth.presentation.schemas.signed_request_headers import SignedRequestHeaders
from integration_auth.protocol.canonicalization.canonical_query import CanonicalQueryEncoder
from tests.support.presentation.request_builder import FastApiRequestBuilder


def test_authentication_request_mapper_preserves_raw_path_query_and_body_hash() -> None:
    async def run() -> None:
        body = b'{"sku":"ABC"}'
        request = FastApiRequestBuilder().build(
            method="POST",
            path="/products/item value",
            raw_path=b"/products/item%20value",
            query_string=b"tag=sale&tag=blue%20sky&page=2",
            body=body,
        )
        headers = SignedRequestHeaders(
            client_id="client-123",
            timestamp=1_787_418_000,
            nonce="nonce-123",
            signature="signature-123",
        )
        mapper = FastApiAuthenticationRequestMapper(
            body_hasher=Sha256BodyHasher(),
            query_encoder=CanonicalQueryEncoder(),
        )

        result = await mapper.map(request, headers)

        assert result.client_id.value == "client-123"
        assert result.signature == "signature-123"
        assert result.request.method == "POST"
        assert result.request.path == "/products/item%20value"
        assert result.request.canonical_query == "page=2&tag=blue%20sky&tag=sale"
        assert result.request.body_sha256 == Sha256BodyHasher().hash(body)

    asyncio.run(run())


def test_authentication_request_mapper_falls_back_to_decoded_path_without_raw_path() -> None:
    async def run() -> None:
        request = FastApiRequestBuilder().build(path="/products/item")
        del request.scope["raw_path"]
        headers = SignedRequestHeaders(
            client_id="client-123",
            timestamp=1_787_418_000,
            nonce="nonce-123",
            signature="signature-123",
        )
        mapper = FastApiAuthenticationRequestMapper(
            body_hasher=Sha256BodyHasher(),
            query_encoder=CanonicalQueryEncoder(),
        )

        result = await mapper.map(request, headers)

        assert result.request.path == "/products/item"

    asyncio.run(run())
