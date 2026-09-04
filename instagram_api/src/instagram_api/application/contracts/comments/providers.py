"""Provider contracts for Instagram comment reads."""

from typing import Protocol

from instagram_api.domain import (
    InstagramComment,
    InstagramCommentId,
    InstagramConnectionId,
    InstagramMediaId,
    Page,
    PaginationCursor,
)


class InstagramCommentProvider(Protocol):
    """Reads normalized comments through one explicit provider connection."""

    async def list_comments(
        self,
        connection_id: InstagramConnectionId,
        media_id: InstagramMediaId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramComment]:
        """Return one page of comments for owned media."""
        ...

    async def list_replies(
        self,
        connection_id: InstagramConnectionId,
        comment_id: InstagramCommentId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramComment]:
        """Return one page of replies for a comment."""
        ...
