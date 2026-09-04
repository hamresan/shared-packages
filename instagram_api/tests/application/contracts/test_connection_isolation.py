"""Connection isolation tests for Stage 1 contracts."""

import asyncio
from datetime import UTC, datetime

import pytest

from instagram_api.domain import (
    InstagramAccount,
    InstagramAccountId,
    InstagramComment,
    InstagramCommentId,
    InstagramConnection,
    InstagramConnectionId,
    InstagramConversation,
    InstagramConversationId,
    InstagramMedia,
    InstagramMediaId,
    InstagramMediaType,
    InstagramMessage,
    InstagramMessageId,
    InstagramMessageSendRequest,
    InstagramUserId,
)
from tests.fakes import (
    FakeInstagramAccessTokenProvider,
    FakeInstagramAccountReader,
    FakeInstagramCommentReader,
    FakeInstagramCommentReplier,
    FakeInstagramConnectionReader,
    FakeInstagramConversationReader,
    FakeInstagramMediaReader,
    FakeInstagramMessageReader,
    FakeInstagramMessageSender,
)


def test_two_connections_remain_isolated_across_read_contracts() -> None:
    first_connection_id = InstagramConnectionId("connection-a")
    second_connection_id = InstagramConnectionId("connection-b")
    first_account_id = InstagramAccountId("ig-account-a")
    second_account_id = InstagramAccountId("ig-account-b")

    connection_reader = FakeInstagramConnectionReader(
        {
            first_connection_id: InstagramConnection(
                id=first_connection_id,
                provider_account_id=first_account_id,
                permissions=frozenset({"instagram_business_basic"}),
                is_usable=True,
            ),
            second_connection_id: InstagramConnection(
                id=second_connection_id,
                provider_account_id=second_account_id,
                permissions=frozenset({"instagram_business_basic"}),
                is_usable=True,
            ),
        }
    )
    token_provider = FakeInstagramAccessTokenProvider(
        {
            first_connection_id: "token-a",
            second_connection_id: "token-b",
        }
    )
    account_reader = FakeInstagramAccountReader(
        {
            first_connection_id: InstagramAccount(id=first_account_id, username="account_a"),
            second_connection_id: InstagramAccount(id=second_account_id, username="account_b"),
        }
    )

    first_connection = asyncio.run(connection_reader.get_connection(first_connection_id))
    second_connection = asyncio.run(connection_reader.get_connection(second_connection_id))
    first_token = asyncio.run(token_provider.get_access_token(first_connection_id))
    second_token = asyncio.run(token_provider.get_access_token(second_connection_id))
    first_account = asyncio.run(account_reader.get_account(first_connection_id))
    second_account = asyncio.run(account_reader.get_account(second_connection_id))

    assert first_connection.provider_account_id == first_account_id
    assert second_connection.provider_account_id == second_account_id
    assert first_token == "token-a"
    assert second_token == "token-b"
    assert first_account.username == "account_a"
    assert second_account.username == "account_b"
    assert token_provider.requested_connection_ids == [first_connection_id, second_connection_id]


def test_two_connections_remain_isolated_for_media_messages_and_comments() -> None:
    now = datetime.now(UTC)
    first_connection_id = InstagramConnectionId("connection-a")
    second_connection_id = InstagramConnectionId("connection-b")
    first_media_id = InstagramMediaId("media-a")
    second_media_id = InstagramMediaId("media-b")
    first_conversation_id = InstagramConversationId("conversation-a")
    second_conversation_id = InstagramConversationId("conversation-b")
    first_user_id = InstagramUserId("user-a")
    second_user_id = InstagramUserId("user-b")
    first_comment_id = InstagramCommentId("comment-a")
    second_comment_id = InstagramCommentId("comment-b")

    media_reader = FakeInstagramMediaReader(
        {
            first_connection_id: (
                InstagramMedia(first_media_id, InstagramMediaType.IMAGE, now, caption="A"),
            ),
            second_connection_id: (
                InstagramMedia(second_media_id, InstagramMediaType.REEL, now, caption="B"),
            ),
        }
    )
    conversation_reader = FakeInstagramConversationReader(
        {
            first_connection_id: (
                InstagramConversation(first_conversation_id, (first_user_id,), now),
            ),
            second_connection_id: (
                InstagramConversation(second_conversation_id, (second_user_id,), now),
            ),
        }
    )
    message_reader = FakeInstagramMessageReader(
        {
            (first_connection_id, first_conversation_id): (
                InstagramMessage(
                    InstagramMessageId("message-a"),
                    first_conversation_id,
                    first_user_id,
                    now,
                    "A",
                ),
            ),
            (second_connection_id, second_conversation_id): (
                InstagramMessage(
                    InstagramMessageId("message-b"),
                    second_conversation_id,
                    second_user_id,
                    now,
                    "B",
                ),
            ),
        }
    )
    comment_reader = FakeInstagramCommentReader(
        comments={
            (first_connection_id, first_media_id): (
                InstagramComment(first_comment_id, first_media_id, first_user_id, "A", now),
            ),
            (second_connection_id, second_media_id): (
                InstagramComment(second_comment_id, second_media_id, second_user_id, "B", now),
            ),
        },
        replies={
            (first_connection_id, first_comment_id): (),
            (second_connection_id, second_comment_id): (),
        },
    )

    first_media = asyncio.run(media_reader.list_media(first_connection_id)).items
    second_media = asyncio.run(media_reader.list_media(second_connection_id)).items
    first_conversations = asyncio.run(
        conversation_reader.list_conversations(first_connection_id)
    ).items
    second_messages = asyncio.run(
        message_reader.list_messages(second_connection_id, second_conversation_id)
    ).items
    first_comments = asyncio.run(
        comment_reader.list_comments(first_connection_id, first_media_id)
    ).items

    assert first_media[0].id == first_media_id
    assert second_media[0].id == second_media_id
    assert first_conversations[0].id == first_conversation_id
    assert second_messages[0].conversation_id == second_conversation_id
    assert first_comments[0].id == first_comment_id


def test_write_contracts_record_the_explicit_connection() -> None:
    connection_id = InstagramConnectionId("connection-a")
    recipient_id = InstagramUserId("recipient-a")
    comment_id = InstagramCommentId("comment-a")
    sender = FakeInstagramMessageSender()
    replier = FakeInstagramCommentReplier()

    send_result = asyncio.run(
        sender.send_message(
            connection_id,
            InstagramMessageSendRequest(recipient_id=recipient_id, text="Hello"),
        )
    )
    public_result = asyncio.run(replier.reply_publicly(connection_id, comment_id, "Public"))
    private_result = asyncio.run(replier.reply_privately(connection_id, comment_id, "Private"))

    assert send_result.message_id == InstagramMessageId("sent-1")
    assert sender.sent[0][0] == connection_id
    assert public_result.comment_id == InstagramCommentId("public-reply")
    assert private_result.comment_id == InstagramCommentId("private-reply")
    assert replier.public_replies == [(connection_id, comment_id, "Public")]
    assert replier.private_replies == [(connection_id, comment_id, "Private")]


def test_fakes_fail_closed_for_unknown_connection_or_target() -> None:
    known_connection_id = InstagramConnectionId("known")
    missing_connection_id = InstagramConnectionId("missing")
    media_id = InstagramMediaId("media")
    media_reader = FakeInstagramMediaReader({known_connection_id: ()})
    token_provider = FakeInstagramAccessTokenProvider({known_connection_id: "token"})

    with pytest.raises(KeyError):
        asyncio.run(token_provider.get_access_token(missing_connection_id))

    with pytest.raises(KeyError):
        asyncio.run(media_reader.get_media(known_connection_id, media_id))
