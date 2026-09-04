"""Meta request executor tests."""

import asyncio

import pytest

from instagram_api.domain import InstagramConnectionId
from instagram_api.infrastructure.meta.http import (
    MetaApiConfig,
    MetaErrorDecoder,
    MetaHttpMethod,
    MetaHttpResponse,
    MetaRateLimitError,
    MetaRequestBuilder,
    MetaRequestExecutor,
    MetaResponseDecoder,
    MetaRetryPolicy,
)
from tests.fakes import FakeInstagramAccessTokenProvider
from tests.infrastructure.meta.http.fakes import (
    RecordingMetaHttpObserver,
    SequenceMetaHttpTransport,
)


def build_executor(
    *,
    transport: SequenceMetaHttpTransport,
    observer: RecordingMetaHttpObserver,
    retry_policy: MetaRetryPolicy | None = None,
) -> MetaRequestExecutor:
    connection_id = InstagramConnectionId("connection-a")
    token_provider = FakeInstagramAccessTokenProvider({connection_id: "top-secret"})
    return MetaRequestExecutor(
        request_builder=MetaRequestBuilder(
            MetaApiConfig(api_version="v24.0"),
            token_provider,
        ),
        transport=transport,
        decoder=MetaResponseDecoder(MetaErrorDecoder()),
        retry_policy=retry_policy or MetaRetryPolicy(base_delay_seconds=0),
        observer=observer,
    )


def test_executor_retries_safe_get_and_never_exposes_token_to_observer() -> None:
    observer = RecordingMetaHttpObserver()
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                429,
                {},
                b'{"error":{"message":"limited","code":4}}',
            ),
            MetaHttpResponse(200, {}, b'{"id":"ok"}'),
        ]
    )
    executor = build_executor(transport=transport, observer=observer)

    result = asyncio.run(
        executor.execute_json(
            connection_id=InstagramConnectionId("connection-a"),
            method=MetaHttpMethod.GET,
            path="me",
        )
    )

    assert result == {"id": "ok"}
    assert len(transport.requests) == 2
    assert len(observer.started) == 2
    assert len(observer.failures) == 1
    assert all(
        connection_id == InstagramConnectionId("connection-a")
        for connection_id, _, _ in observer.started
    )
    assert all("top-secret" not in url for _, _, url in observer.started)
    assert all("top-secret" not in url for _, _, url, _ in observer.responses)
    assert observer.responses[0] == (
        InstagramConnectionId("connection-a"),
        "GET",
        "https://graph.instagram.com/v24.0/me",
        429,
    )
    assert observer.failures[0][0] == InstagramConnectionId("connection-a")
    assert observer.failures[0][-1] == "MetaRateLimitError"


def test_executor_does_not_retry_non_idempotent_post() -> None:
    observer = RecordingMetaHttpObserver()
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                429,
                {},
                b'{"error":{"message":"limited","code":4}}',
            )
        ]
    )
    executor = build_executor(transport=transport, observer=observer)

    with pytest.raises(MetaRateLimitError):
        asyncio.run(
            executor.execute_json(
                connection_id=InstagramConnectionId("connection-a"),
                method=MetaHttpMethod.POST,
                path="messages",
                json_body={"message": "hello"},
            )
        )

    assert len(transport.requests) == 1
