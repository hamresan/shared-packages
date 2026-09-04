"""HTTPX Meta transport tests."""

import asyncio

import httpx
import pytest

from instagram_api.infrastructure.meta.http import (
    HttpxMetaHttpTransport,
    MetaHttpMethod,
    MetaHttpRequest,
    MetaTimeoutConfig,
    MetaTimeoutError,
)


def test_httpx_transport_executes_request_without_leaking_client_types() -> None:
    seen_authorization: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_authorization.append(request.headers["Authorization"])
        return httpx.Response(200, json={"ok": True})

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            transport = HttpxMetaHttpTransport(client, MetaTimeoutConfig())
            response = await transport.send(
                MetaHttpRequest(
                    method=MetaHttpMethod.GET,
                    url="https://graph.instagram.com/v24.0/me",
                    headers={"Authorization": "Bearer secret"},
                )
            )
            assert response.status_code == 200
            assert response.body == b'{"ok":true}'

    asyncio.run(run())
    assert seen_authorization == ["Bearer secret"]


def test_httpx_transport_normalizes_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout", request=request)

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            transport = HttpxMetaHttpTransport(client, MetaTimeoutConfig(read_seconds=0.1))
            with pytest.raises(MetaTimeoutError):
                await transport.send(
                    MetaHttpRequest(
                        method=MetaHttpMethod.GET,
                        url="https://graph.instagram.com/v24.0/me",
                    )
                )

    asyncio.run(run())
