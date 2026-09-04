"""Meta Instagram media provider tests."""

import asyncio

import pytest

from instagram_api.application.media import InstagramMediaUnavailableError
from instagram_api.domain import InstagramConnectionId, InstagramMediaId, InstagramMediaType
from instagram_api.infrastructure.meta.http import (
    MetaApiConfig,
    MetaErrorDecoder,
    MetaHttpResponse,
    MetaPaginationCursorMapper,
    MetaRequestBuilder,
    MetaRequestExecutor,
    MetaResponseDecoder,
    MetaRetryPolicy,
    NullMetaHttpObserver,
)
from instagram_api.infrastructure.meta.media import (
    MEDIA_FIELDS,
    MetaInstagramMediaErrorMapper,
    MetaInstagramMediaFieldParser,
    MetaInstagramMediaMapper,
    MetaInstagramMediaPayloadParser,
    MetaInstagramMediaProvider,
    MetaInstagramMediaTimestampParser,
    MetaInstagramMediaTypeMapper,
)
from tests.fakes import FakeInstagramAccessTokenProvider
from tests.infrastructure.meta.http.fakes import SequenceMetaHttpTransport


def build_provider(
    transport: SequenceMetaHttpTransport,
    connection_id: InstagramConnectionId,
) -> MetaInstagramMediaProvider:
    executor = MetaRequestExecutor(
        request_builder=MetaRequestBuilder(
            MetaApiConfig(api_version="v24.0"),
            FakeInstagramAccessTokenProvider({connection_id: "token"}),
        ),
        transport=transport,
        decoder=MetaResponseDecoder(MetaErrorDecoder()),
        retry_policy=MetaRetryPolicy(base_delay_seconds=0),
        observer=NullMetaHttpObserver(),
    )
    return MetaInstagramMediaProvider(
        executor,
        MetaInstagramMediaPayloadParser(MetaInstagramMediaFieldParser()),
        MetaInstagramMediaMapper(
            MetaInstagramMediaTypeMapper(),
            MetaInstagramMediaTimestampParser(),
        ),
        MetaPaginationCursorMapper(),
        MetaInstagramMediaErrorMapper(),
    )


def test_provider_lists_media_with_cursor_and_maps_next_cursor() -> None:
    connection_id = InstagramConnectionId("connection")
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                200,
                {},
                (
                    b'{"data":[{"id":"media","media_type":"VIDEO",'
                    b'"media_product_type":"REELS","timestamp":"2026-09-04T10:00:00+0000",'
                    b'"caption":"Reel caption"}],"paging":{"cursors":{"after":"next"}}}'
                ),
            )
        ]
    )
    provider = build_provider(transport, connection_id)

    page = asyncio.run(provider.list_media(connection_id))

    assert page.items[0].media_type is InstagramMediaType.REEL
    assert page.items[0].caption == "Reel caption"
    assert str(page.next_cursor) == "next"
    request = transport.requests[0]
    assert request.url.endswith("/v24.0/me/media")
    assert request.params["fields"] == ",".join(MEDIA_FIELDS)


def test_provider_passes_after_cursor_and_reads_media_detail() -> None:
    connection_id = InstagramConnectionId("connection")
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(200, {}, b'{"data":[],"paging":{"cursors":{}}}'),
            MetaHttpResponse(
                200,
                {},
                b'{"id":"media","media_type":"IMAGE","timestamp":"2026-09-04T10:00:00+0000"}',
            ),
        ]
    )
    provider = build_provider(transport, connection_id)

    asyncio.run(provider.list_media(connection_id, cursor="cursor"))
    media = asyncio.run(provider.get_media(connection_id, InstagramMediaId("media")))

    assert transport.requests[0].params["after"] == "cursor"
    assert media.id == InstagramMediaId("media")
    assert transport.requests[1].url.endswith("/v24.0/media")


def test_provider_maps_deleted_or_unavailable_media_explicitly() -> None:
    connection_id = InstagramConnectionId("connection")
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                400,
                {},
                b'{"error":{"message":"Unsupported get request","code":100}}',
            )
        ]
    )
    provider = build_provider(transport, connection_id)

    with pytest.raises(InstagramMediaUnavailableError):
        asyncio.run(provider.get_media(connection_id, InstagramMediaId("missing")))
