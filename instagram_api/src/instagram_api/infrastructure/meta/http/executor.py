"""Shared Meta request execution orchestration."""

import asyncio
from collections.abc import Mapping

from instagram_api.domain import InstagramConnectionId

from .contracts import MetaHttpObserver, MetaHttpTransport
from .decoder import MetaResponseDecoder
from .models import MetaHttpMethod
from .request_builder import MetaRequestBuilder
from .retry import MetaRetryPolicy


class MetaRequestExecutor:
    """Coordinates request building, transport, decoding, retry, and observability."""

    def __init__(
        self,
        request_builder: MetaRequestBuilder,
        transport: MetaHttpTransport,
        decoder: MetaResponseDecoder,
        retry_policy: MetaRetryPolicy,
        observer: MetaHttpObserver,
    ) -> None:
        self._request_builder = request_builder
        self._transport = transport
        self._decoder = decoder
        self._retry_policy = retry_policy
        self._observer = observer

    async def execute_json(
        self,
        *,
        connection_id: InstagramConnectionId,
        method: MetaHttpMethod,
        path: str,
        params: Mapping[str, str] | None = None,
        json_body: Mapping[str, object] | None = None,
    ) -> Mapping[str, object]:
        """Execute one provider request for the selected connection."""

        request = await self._request_builder.build(
            connection_id=connection_id,
            method=method,
            path=path,
            params=params,
            json_body=json_body,
        )
        attempt = 1

        while True:
            self._observer.request_started(method=request.method.value, url=request.url)
            try:
                response = await self._transport.send(request)
                self._observer.response_received(
                    method=request.method.value,
                    url=request.url,
                    status_code=response.status_code,
                )
                return self._decoder.decode_json(response)
            except Exception as exc:
                self._observer.request_failed(
                    method=request.method.value,
                    url=request.url,
                    error_type=type(exc).__name__,
                )
                if not self._retry_policy.should_retry(
                    method=request.method,
                    error=exc,
                    attempt=attempt,
                ):
                    raise

                delay_seconds = self._retry_policy.delay_seconds(attempt)
                attempt += 1
                await asyncio.sleep(delay_seconds)
