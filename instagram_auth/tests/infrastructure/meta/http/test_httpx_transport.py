from asyncio import run

import httpx
import pytest

from instagram_auth.infrastructure.meta.http import (
    HttpxMetaHttpTransport,
    MetaTransportError,
    MetaTransportTimeoutError,
)


def test_httpx_transport_maps_json_response() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"access_token": "token"})

    async def execute() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            response = await HttpxMetaHttpTransport(client).post_form(
                url="https://api.instagram.com/oauth/access_token",
                data={"code": "code"},
            )
        assert response.status_code == 200
        assert response.payload == {"access_token": "token"}

    run(execute())


def test_httpx_transport_maps_timeout_without_request_content() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("secret-token", request=request)

    async def execute() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(MetaTransportTimeoutError) as exc_info:
                await HttpxMetaHttpTransport(client).get(
                    url="https://graph.instagram.com/me", params={}
                )
        assert "secret-token" not in str(exc_info.value)

    run(execute())


def test_httpx_transport_maps_request_error() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("provider down", request=request)

    async def execute() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(MetaTransportError):
                await HttpxMetaHttpTransport(client).get(
                    url="https://graph.instagram.com/me", params={}
                )

    run(execute())
