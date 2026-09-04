"""HTTPX implementation of the shared Meta HTTP transport."""

import httpx

from .config import MetaTimeoutConfig
from .contracts import MetaHttpTransport
from .errors import MetaTimeoutError
from .models import MetaHttpRequest, MetaHttpResponse


class HttpxMetaHttpTransport(MetaHttpTransport):
    """Executes Meta requests through an injected HTTPX async client."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        timeout: MetaTimeoutConfig,
    ) -> None:
        self._client = client
        self._timeout = timeout

    async def send(self, request: MetaHttpRequest) -> MetaHttpResponse:
        try:
            response = await self._client.request(
                method=request.method.value,
                url=request.url,
                headers=request.headers,
                params=request.params,
                json=request.json_body,
                timeout=httpx.Timeout(
                    connect=self._timeout.connect_seconds,
                    read=self._timeout.read_seconds,
                    write=self._timeout.write_seconds,
                    pool=self._timeout.pool_seconds,
                ),
            )
        except httpx.TimeoutException as exc:
            raise MetaTimeoutError(
                message="Meta provider request timed out.",
                status_code=0,
            ) from exc

        return MetaHttpResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            body=response.content,
        )
