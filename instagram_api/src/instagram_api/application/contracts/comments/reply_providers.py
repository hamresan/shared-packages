"""Provider boundaries for Instagram comment reply operations."""

from typing import Protocol

from instagram_api.domain import (
    InstagramCommentId,
    InstagramCommentReplyResult,
    InstagramConnectionId,
    InstagramPrivateCommentReplyRequest,
    InstagramPrivateCommentReplyResult,
)


class InstagramPublicCommentReplyProvider(Protocol):
    """Publishes public replies for one explicit connection."""

    async def reply(
        self,
        connection_id: InstagramConnectionId,
        comment_id: InstagramCommentId,
        text: str,
    ) -> InstagramCommentReplyResult:
        """Publish a public comment reply."""
        ...


class InstagramPrivateCommentReplyProvider(Protocol):
    """Publishes private replies for one explicit connection."""

    async def reply(
        self,
        connection_id: InstagramConnectionId,
        request: InstagramPrivateCommentReplyRequest,
    ) -> InstagramPrivateCommentReplyResult:
        """Publish a private reply to an eligible commenter."""
        ...
