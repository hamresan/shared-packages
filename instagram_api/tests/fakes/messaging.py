"""Messaging contract fakes."""

from instagram_api.application.contracts.messaging import (
    InstagramConversationProvider,
    InstagramConversationReader,
    InstagramMessageProvider,
    InstagramMessageReader,
    InstagramMessageRecipientEligibilityChecker,
    InstagramMessageSender,
    InstagramOutboundMessageProvider,
)
from instagram_api.domain import (
    InstagramConnectionId,
    InstagramConversation,
    InstagramConversationId,
    InstagramMessage,
    InstagramMessageId,
    InstagramMessageSendRequest,
    InstagramMessageSendResult,
    InstagramUserId,
    Page,
    PaginationCursor,
)


class FakeInstagramConversationReader(InstagramConversationReader):
    """Fake conversation reader isolated by connection ID."""

    def __init__(
        self,
        conversations: dict[InstagramConnectionId, tuple[InstagramConversation, ...]],
    ) -> None:
        self._conversations = conversations

    async def list_conversations(
        self,
        connection_id: InstagramConnectionId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramConversation]:
        del cursor
        return Page(items=self._conversations[connection_id])


class FakeInstagramConversationProvider(InstagramConversationProvider):
    """Fake conversation provider isolated by connection ID."""

    def __init__(
        self,
        pages: dict[InstagramConnectionId, Page[InstagramConversation]],
    ) -> None:
        self._pages = pages
        self.calls: list[tuple[InstagramConnectionId, PaginationCursor | None]] = []

    async def list_conversations(
        self,
        connection_id: InstagramConnectionId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramConversation]:
        self.calls.append((connection_id, cursor))
        return self._pages[connection_id]


class FakeInstagramMessageReader(InstagramMessageReader):
    """Fake message reader isolated by connection and conversation."""

    def __init__(
        self,
        messages: dict[
            tuple[InstagramConnectionId, InstagramConversationId],
            tuple[InstagramMessage, ...],
        ],
    ) -> None:
        self._messages = messages

    async def list_messages(
        self,
        connection_id: InstagramConnectionId,
        conversation_id: InstagramConversationId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramMessage]:
        del cursor
        return Page(items=self._messages[(connection_id, conversation_id)])


class FakeInstagramMessageProvider(InstagramMessageProvider):
    """Fake message provider isolated by connection and conversation."""

    def __init__(
        self,
        pages: dict[
            tuple[InstagramConnectionId, InstagramConversationId],
            Page[InstagramMessage],
        ],
    ) -> None:
        self._pages = pages
        self.calls: list[
            tuple[
                InstagramConnectionId,
                InstagramConversationId,
                PaginationCursor | None,
            ]
        ] = []

    async def list_messages(
        self,
        connection_id: InstagramConnectionId,
        conversation_id: InstagramConversationId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramMessage]:
        self.calls.append((connection_id, conversation_id, cursor))
        return self._pages[(connection_id, conversation_id)]


class FakeInstagramMessageRecipientEligibilityChecker(
    InstagramMessageRecipientEligibilityChecker
):
    """Fake recipient eligibility checker scoped by connection and recipient."""

    def __init__(
        self,
        eligibility: dict[tuple[InstagramConnectionId, InstagramUserId], bool],
    ) -> None:
        self._eligibility = eligibility
        self.calls: list[tuple[InstagramConnectionId, InstagramUserId]] = []

    async def is_eligible(
        self,
        connection_id: InstagramConnectionId,
        recipient_id: InstagramUserId,
    ) -> bool:
        self.calls.append((connection_id, recipient_id))
        return self._eligibility[(connection_id, recipient_id)]


class FakeInstagramOutboundMessageProvider(InstagramOutboundMessageProvider):
    """Fake outbound provider that records explicit connection routing."""

    def __init__(self) -> None:
        self.calls: list[tuple[InstagramConnectionId, InstagramMessageSendRequest]] = []

    async def send_message(
        self,
        connection_id: InstagramConnectionId,
        request: InstagramMessageSendRequest,
    ) -> InstagramMessageSendResult:
        self.calls.append((connection_id, request))
        return InstagramMessageSendResult(
            message_id=InstagramMessageId(f"sent-{len(self.calls)}"),
            recipient_id=request.recipient_id,
        )


class FakeInstagramMessageSender(InstagramMessageSender):
    """Fake sender that records the selected connection."""

    def __init__(self) -> None:
        self.sent: list[tuple[InstagramConnectionId, InstagramMessageSendRequest]] = []

    async def send_message(
        self,
        connection_id: InstagramConnectionId,
        request: InstagramMessageSendRequest,
    ) -> InstagramMessageSendResult:
        self.sent.append((connection_id, request))
        return InstagramMessageSendResult(
            message_id=InstagramMessageId(f"sent-{len(self.sent)}"),
            recipient_id=request.recipient_id,
            correlation_id=request.correlation_id,
        )
