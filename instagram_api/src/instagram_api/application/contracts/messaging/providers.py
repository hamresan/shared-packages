"""Provider boundaries for Instagram conversation and message reads."""

from typing import Protocol

from instagram_api.domain import (
    InstagramConnectionId,
    InstagramConversation,
    InstagramConversationId,
    InstagramMessage,
    Page,
    PaginationCursor,
)


class InstagramConversationProvider(Protocol):
    """Reads normalized conversations for one explicit connection."""

    async def list_conversations(
        self,
        connection_id: InstagramConnectionId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramConversation]:
        """Return one page of conversations."""
        ...


class InstagramMessageProvider(Protocol):
    """Reads normalized messages for one explicit connection."""

    async def list_messages(
        self,
        connection_id: InstagramConnectionId,
        conversation_id: InstagramConversationId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramMessage]:
        """Return one page of messages."""
        ...
