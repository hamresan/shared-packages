"""Instagram messaging service tests."""

import asyncio
from datetime import UTC, datetime

import pytest

from instagram_api.application.messaging import (
    InstagramConversationService,
    InstagramMessageService,
    InstagramMessagingPermissionRequiredError,
    InstagramMessagingReadPolicy,
)
from instagram_api.domain import (
    InstagramAccountId,
    InstagramConnection,
    InstagramConnectionId,
    InstagramConversation,
    InstagramConversationId,
    InstagramMessage,
    InstagramMessageId,
    InstagramUserId,
    Page,
    PaginationCursor,
)
from tests.fakes import (
    FakeInstagramConnectionReader,
    FakeInstagramConversationProvider,
    FakeInstagramMessageProvider,
)


def test_services_keep_two_connections_isolated_and_forward_cursors() -> None:
    first_id = InstagramConnectionId("connection-a")
    second_id = InstagramConnectionId("connection-b")
    first_conversation = InstagramConversation(InstagramConversationId("conversation-a"), ())
    second_conversation = InstagramConversation(InstagramConversationId("conversation-b"), ())
    now = datetime.now(UTC)
    first_message = InstagramMessage(
        InstagramMessageId("message-a"),
        first_conversation.id,
        InstagramUserId("sender-a"),
        now,
        "A",
    )
    second_message = InstagramMessage(
        InstagramMessageId("message-b"),
        second_conversation.id,
        InstagramUserId("sender-b"),
        now,
        "B",
    )
    connections = FakeInstagramConnectionReader(
        {
            first_id: InstagramConnection(
                first_id,
                InstagramAccountId("account-a"),
                frozenset(
                    {
                        "instagram_business_basic",
                        "instagram_business_manage_messages",
                    }
                ),
                True,
            ),
            second_id: InstagramConnection(
                second_id,
                InstagramAccountId("account-b"),
                frozenset(
                    {
                        "instagram_business_basic",
                        "instagram_business_manage_messages",
                    }
                ),
                True,
            ),
        }
    )
    conversation_provider = FakeInstagramConversationProvider(
        {
            first_id: Page((first_conversation,)),
            second_id: Page((second_conversation,)),
        }
    )
    message_provider = FakeInstagramMessageProvider(
        {
            (first_id, first_conversation.id): Page((first_message,)),
            (second_id, second_conversation.id): Page((second_message,)),
        }
    )
    policy = InstagramMessagingReadPolicy()
    conversations = InstagramConversationService(connections, conversation_provider, policy)
    messages = InstagramMessageService(connections, message_provider, policy)

    first_page = asyncio.run(
        conversations.list_conversations(first_id, PaginationCursor("conversation-cursor"))
    )
    second_page = asyncio.run(
        messages.list_messages(
            second_id,
            second_conversation.id,
            PaginationCursor("message-cursor"),
        )
    )

    assert first_page.items == (first_conversation,)
    assert second_page.items == (second_message,)
    assert conversation_provider.calls == [
        (first_id, PaginationCursor("conversation-cursor"))
    ]
    assert message_provider.calls == [
        (
            second_id,
            second_conversation.id,
            PaginationCursor("message-cursor"),
        )
    ]


def test_service_rejects_missing_permission_before_provider_call() -> None:
    connection_id = InstagramConnectionId("connection")
    conversation_id = InstagramConversationId("conversation")
    provider = FakeInstagramMessageProvider(
        {(connection_id, conversation_id): Page(items=())}
    )
    service = InstagramMessageService(
        FakeInstagramConnectionReader(
            {
                connection_id: InstagramConnection(
                    connection_id,
                    InstagramAccountId("account"),
                    frozenset({"instagram_business_basic"}),
                    True,
                )
            }
        ),
        provider,
        InstagramMessagingReadPolicy(),
    )

    with pytest.raises(InstagramMessagingPermissionRequiredError):
        asyncio.run(service.list_messages(connection_id, conversation_id))

    assert provider.calls == []
