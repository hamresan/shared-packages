"""Instagram comment reply contracts."""

from typing import Protocol

from instagram_api.domain.comments import InstagramCommentReplyResult
from instagram_api.domain.identifiers import InstagramCommentId, InstagramConnectionId


class InstagramCommentReplier(Protocol):
    """Publishes replies through one explicit Instagram connection."""

    async def reply_publicly(
        self,
        connection_id: InstagramConnectionId,
        comment_id: InstagramCommentId,
        text: str,
    ) -> InstagramCommentReplyResult:
        """Publish a public reply to the requested comment."""
        ...

    async def reply_privately(
        self,
        connection_id: InstagramConnectionId,
        comment_id: InstagramCommentId,
        text: str,
    ) -> InstagramCommentReplyResult:
        """Publish an eligible private reply to the requested commenter."""
        ...
