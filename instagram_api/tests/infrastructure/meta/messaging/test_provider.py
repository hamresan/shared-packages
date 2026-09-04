"""Meta conversation and message provider tests."""

import asyncio

from instagram_api.domain import (
    InstagramConnectionId,
    InstagramConversationId,
    PaginationCursor,
)
from instagram_api.infrastructure.meta.http import MetaHttpResponse
from tests.infrastructure.meta.http.fakes import SequenceMetaHttpTransport
from tests.infrastructure.meta.messaging.factories import build_meta_messaging_providers


def test_conversation_provider_uses_instagram_platform_and_cursor() -> None:
    connection_id = InstagramConnectionId("connection")
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                200,
                {},
                (
                    b'{"data":[{"id":"conversation","updated_time":'
                    b'"2026-09-04T10:00:00+0000"}],"paging":{"cursors":{"after":"next"}}}'
                ),
            )
        ]
    )
    conversation_provider, _ = build_meta_messaging_providers(transport, connection_id)

    page = asyncio.run(
        conversation_provider.list_conversations(
            connection_id,
            PaginationCursor("cursor"),
        )
    )

    assert page.items[0].id == InstagramConversationId("conversation")
    assert page.next_cursor == PaginationCursor("next")
    request = transport.requests[0]
    assert request.url.endswith("/v24.0/me/conversations")
    assert request.params["platform"] == "instagram"
    assert request.params["after"] == "cursor"


def test_message_provider_reads_details_and_nested_pagination() -> None:
    connection_id = InstagramConnectionId("connection")
    conversation_id = InstagramConversationId("conversation")
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                200,
                {},
                (
                    b'{"messages":{"data":[{"id":"message","created_time":'
                    b'"2026-09-04T10:01:00+0000","is_unsupported":false}],'
                    b'"paging":{"cursors":{"after":"next"}}},"id":"conversation"}'
                ),
            ),
            MetaHttpResponse(
                200,
                {},
                (
                    b'{"id":"message","created_time":"2026-09-04T10:01:00+0000",'
                    b'"from":{"id":"sender"},"message":"hello"}'
                ),
            ),
        ]
    )
    _, message_provider = build_meta_messaging_providers(transport, connection_id)

    page = asyncio.run(
        message_provider.list_messages(
            connection_id,
            conversation_id,
            PaginationCursor("cursor"),
        )
    )

    assert page.items[0].text == "hello"
    assert page.items[0].details_available is True
    assert page.next_cursor == PaginationCursor("next")
    assert transport.requests[0].params["fields"] == "messages.after(cursor)"
    assert transport.requests[1].params["fields"] == "id,created_time,from,to,message"


def test_message_provider_preserves_unsupported_message_without_detail_request() -> None:
    connection_id = InstagramConnectionId("connection")
    conversation_id = InstagramConversationId("conversation")
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                200,
                {},
                (
                    b'{"messages":{"data":[{"id":"message","created_time":'
                    b'"2026-09-04T10:01:00+0000","is_unsupported":true}]}}'
                ),
            )
        ]
    )
    _, message_provider = build_meta_messaging_providers(transport, connection_id)

    page = asyncio.run(message_provider.list_messages(connection_id, conversation_id))

    assert len(transport.requests) == 1
    assert page.items[0].is_unsupported is True
    assert page.items[0].details_available is False
    assert page.items[0].sender_id is None


def test_message_provider_does_not_request_details_for_older_cursor_page() -> None:
    connection_id = InstagramConnectionId("connection")
    conversation_id = InstagramConversationId("conversation")
    transport = SequenceMetaHttpTransport(
        [
            MetaHttpResponse(
                200,
                {},
                (
                    b'{"messages":{"data":[{"id":"old-message","created_time":'
                    b'"2026-01-01T10:01:00+0000","is_unsupported":false}]}}'
                ),
            )
        ]
    )
    _, message_provider = build_meta_messaging_providers(transport, connection_id)

    page = asyncio.run(
        message_provider.list_messages(
            connection_id,
            conversation_id,
            PaginationCursor("older-page"),
        )
    )

    assert len(transport.requests) == 1
    assert page.items[0].id.value == "old-message" if hasattr(page.items[0].id, "value") else str(page.items[0].id) == "old-message"
    assert page.items[0].details_available is False
    assert page.items[0].sender_id is None
