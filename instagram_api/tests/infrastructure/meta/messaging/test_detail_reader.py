"""Meta message-detail availability tests."""

import asyncio

import pytest

from instagram_api.domain import InstagramConnectionId
from instagram_api.infrastructure.meta.http import MetaHttpResponse, MetaProviderError
from instagram_api.infrastructure.meta.messaging import MetaInstagramMessageSummaryDto
from tests.infrastructure.meta.http.fakes import SequenceMetaHttpTransport
from tests.infrastructure.meta.messaging.factories import build_meta_message_detail_reader


def test_detail_reader_skips_messages_beyond_documented_detail_limit() -> None:
    connection_id = InstagramConnectionId("connection")
    transport = SequenceMetaHttpTransport([])
    reader = build_meta_message_detail_reader(transport, connection_id)
    summary = MetaInstagramMessageSummaryDto(
        id="old-message",
        created_time="2026-01-01T10:00:00+0000",
        is_unsupported=False,
    )

    detail = asyncio.run(reader.read(connection_id, summary, position=20))

    assert detail is None
    assert transport.requests == []


def test_detail_reader_skips_unsupported_message() -> None:
    connection_id = InstagramConnectionId("connection")
    transport = SequenceMetaHttpTransport([])
    reader = build_meta_message_detail_reader(transport, connection_id)
    summary = MetaInstagramMessageSummaryDto(
        id="unsupported",
        created_time="2026-09-04T10:00:00+0000",
        is_unsupported=True,
    )

    detail = asyncio.run(reader.read(connection_id, summary, position=0))

    assert detail is None
    assert transport.requests == []


def test_detail_reader_reads_eligible_message() -> None:
    connection_id = InstagramConnectionId("connection")
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                200,
                {},
                (
                    b'{"id":"message","created_time":"2026-09-04T10:00:00+0000",'
                    b'"from":{"id":"sender"},"message":"hello"}'
                ),
            )
        ]
    )
    reader = build_meta_message_detail_reader(transport, connection_id)
    summary = MetaInstagramMessageSummaryDto(
        id="message",
        created_time="2026-09-04T10:00:00+0000",
        is_unsupported=False,
    )

    detail = asyncio.run(reader.read(connection_id, summary, position=0))

    assert detail is not None
    assert detail.sender_id == "sender"
    assert detail.message == "hello"


def test_detail_reader_propagates_provider_error_for_eligible_message() -> None:
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
    reader = build_meta_message_detail_reader(transport, connection_id)
    summary = MetaInstagramMessageSummaryDto(
        id="message",
        created_time="2026-09-04T10:00:00+0000",
        is_unsupported=False,
    )

    with pytest.raises(MetaProviderError):
        asyncio.run(reader.read(connection_id, summary, position=0))
