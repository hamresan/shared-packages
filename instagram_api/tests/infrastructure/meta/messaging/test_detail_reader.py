"""Meta message-detail availability tests."""

import asyncio

import pytest

from instagram_api.domain import InstagramConnectionId
from instagram_api.infrastructure.meta.http import (
    MetaApiConfig,
    MetaErrorDecoder,
    MetaHttpResponse,
    MetaProviderError,
    MetaRequestBuilder,
    MetaRequestExecutor,
    MetaResponseDecoder,
    MetaRetryPolicy,
    NullMetaHttpObserver,
)
from instagram_api.infrastructure.meta.messaging import (
    MetaInstagramMessageDetailAvailabilityPolicy,
    MetaInstagramMessageDetailReader,
    MetaInstagramMessageSummaryDto,
    MetaInstagramMessagingFieldParser,
    MetaInstagramMessagingPayloadParser,
)
from tests.fakes import FakeInstagramAccessTokenProvider
from tests.infrastructure.meta.http.fakes import SequenceMetaHttpTransport


def build_reader(
    transport: SequenceMetaHttpTransport,
    connection_id: InstagramConnectionId,
) -> MetaInstagramMessageDetailReader:
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
    return MetaInstagramMessageDetailReader(
        executor,
        MetaInstagramMessagingPayloadParser(MetaInstagramMessagingFieldParser()),
        MetaInstagramMessageDetailAvailabilityPolicy(),
    )


def test_detail_reader_maps_historical_message_limit_to_missing_details() -> None:
    connection_id = InstagramConnectionId("connection")
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                400,
                {},
                b'{"error":{"message":"deleted","code":100}}',
            )
        ]
    )
    reader = build_reader(transport, connection_id)
    summary = MetaInstagramMessageSummaryDto(
        id="old-message",
        created_time="2026-01-01T10:00:00+0000",
        is_unsupported=False,
    )

    detail = asyncio.run(reader.read(connection_id, summary))

    assert detail is None


def test_detail_reader_propagates_unrecognized_provider_error() -> None:
    connection_id = InstagramConnectionId("connection")
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                400,
                {},
                b'{"error":{"message":"bad request","code":10}}',
            )
        ]
    )
    reader = build_reader(transport, connection_id)
    summary = MetaInstagramMessageSummaryDto(
        id="message",
        created_time="2026-09-04T10:00:00+0000",
        is_unsupported=False,
    )

    with pytest.raises(MetaProviderError):
        asyncio.run(reader.read(connection_id, summary))
