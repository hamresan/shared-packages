"""Meta messaging parser and mapper tests."""

import pytest

from instagram_api.domain import (
    InstagramConversationId,
    InstagramMessageId,
    InstagramUserId,
)
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError
from instagram_api.infrastructure.meta.messaging import (
    MetaInstagramMessagingFieldParser,
    MetaInstagramMessagingMapper,
    MetaInstagramMessagingPayloadParser,
    MetaInstagramMessagingTimestampParser,
)


def test_parser_and_mapper_normalize_conversations_and_message_details() -> None:
    parser = MetaInstagramMessagingPayloadParser(MetaInstagramMessagingFieldParser())
    mapper = MetaInstagramMessagingMapper(MetaInstagramMessagingTimestampParser())

    conversation = mapper.conversation(
        parser.parse_conversations(
            {
                "data": [
                    {
                        "id": "conversation",
                        "updated_time": "2026-09-04T10:00:00+0000",
                    }
                ]
            }
        )[0]
    )
    summary = parser.parse_message_summaries(
        {
            "messages": {
                "data": [
                    {
                        "id": "message",
                        "created_time": "2026-09-04T10:01:00+0000",
                        "is_unsupported": False,
                    }
                ]
            }
        }
    )[0]
    detail = parser.parse_message_detail(
        {
            "id": "message",
            "created_time": "2026-09-04T10:01:00+0000",
            "from": {"id": "sender"},
            "message": "hello",
        }
    )
    message = mapper.message(conversation.id, summary, detail)

    assert conversation.id == InstagramConversationId("conversation")
    assert conversation.participant_ids == ()
    assert message.id == InstagramMessageId("message")
    assert message.sender_id == InstagramUserId("sender")
    assert message.text == "hello"
    assert message.details_available is True
    assert message.is_unsupported is False


def test_mapper_preserves_unsupported_message_without_invented_details() -> None:
    parser = MetaInstagramMessagingPayloadParser(MetaInstagramMessagingFieldParser())
    mapper = MetaInstagramMessagingMapper(MetaInstagramMessagingTimestampParser())
    summary = parser.parse_message_summaries(
        {
            "messages": {
                "data": [
                    {
                        "id": "message",
                        "created_time": "2026-09-04T10:01:00+0000",
                        "is_unsupported": True,
                    }
                ]
            }
        }
    )[0]

    message = mapper.message(InstagramConversationId("conversation"), summary, None)

    assert message.sender_id is None
    assert message.text is None
    assert message.is_unsupported is True
    assert message.details_available is False


def test_parser_rejects_invalid_collections_and_timestamps() -> None:
    parser = MetaInstagramMessagingPayloadParser(MetaInstagramMessagingFieldParser())
    mapper = MetaInstagramMessagingMapper(MetaInstagramMessagingTimestampParser())

    with pytest.raises(MetaInvalidResponseError):
        parser.parse_conversations({"data": "invalid"})

    summary = parser.parse_message_summaries(
        {
            "messages": {
                "data": [
                    {
                        "id": "message",
                        "created_time": "not-a-timestamp",
                    }
                ]
            }
        }
    )[0]
    with pytest.raises(MetaInvalidResponseError):
        mapper.message(InstagramConversationId("conversation"), summary, None)
