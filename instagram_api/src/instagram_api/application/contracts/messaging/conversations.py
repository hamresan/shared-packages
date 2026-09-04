"""Instagram conversation reading contracts."""

from typing import Protocol

from instagram_api.domain.identifiers import InstagramConnectionId, PaginationCursor
from instagram_api.domain.messaging import InstagramConversation
from instagram_api.domain.pagination import Page


class InstagramConversationReader(Protocol):
    """Reads conversations through one explicit Instagram connection."""

    async def list_conversations(
        self,
        connection_id: InstagramConnectionId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramConversation]:
        """Return one page of conversations for the requested connection."""
        ...
