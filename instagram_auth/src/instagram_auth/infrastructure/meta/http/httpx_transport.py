"""HTTPX implementation of the Meta HTTP transport."""

from collections.abc import Mapping
from typing import cast

import httpx

from .contracts import MetaHttpTransport
from .errors import MetaTransportError, MetaTransportTimeoutError
from .models import MetaHttpResponse


class HttpxMetaHttpTransport(MetaHttpTransport):
    """Execute Meta requests through an injected HTTPX client."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def post_form(self, *, url: str, data: Mapping[str, str]) -> MetaHttpResponse:
        try:
            response = await self._client.post(url, data=data)
        except httpx.TimeoutException as exc:
            raise MetaTransportTimeoutError("Meta request timed out") from exc
        except httpx.RequestError as exc:
            raise MetaTransportError("Meta request failed") from exc
        return MetaHttpResponse(response.status_code, cast(dict[str, object], response.json()))

    async def get(self, *, url: str, params: Mapping[str, str]) -> MetaHttpResponse:
        try:
            response = await self._client.get(url, params=params)
        except httpx.TimeoutException as exc:
            raise MetaTransportTimeoutError("Meta request timed out") from exc
        except httpx.RequestError as exc:
            raise MetaTransportError("Meta request failed") from exc
        return MetaHttpResponse(response.status_code, cast(dict[str, object], response.json()))
