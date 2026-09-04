"""Instagram message reading contracts."""

from typing import Protocol

from instagram_api.domain.identifiers import (
    InstagramConnectionId,
    InstagramConversationId,
    PaginationCursor,
)
from instagram_api.domain.messaging import InstagramMessage
from instagram_api.domain.pagination import Page


class InstagramMessageReader(Protocol):
    """Reads messages through one explicit Instagram connection."""

    async def list_messages(
        self,
        connection_id: InstagramConnectionId,
        conversation_id: InstagramConversationId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramMessage]:
        """Return one page of messages for the requested conversation."""
        ...
