"""Instagram comment reading contracts."""

from typing import Protocol

from instagram_api.domain.comments import InstagramComment
from instagram_api.domain.identifiers import (
    InstagramCommentId,
    InstagramConnectionId,
    InstagramMediaId,
    PaginationCursor,
)
from instagram_api.domain.pagination import Page


class InstagramCommentReader(Protocol):
    """Reads comments and replies through one explicit connection."""

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
