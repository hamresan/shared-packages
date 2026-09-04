"""Instagram comment reply use-case contracts."""

from typing import Protocol

from instagram_api.domain import (
    InstagramCommentId,
    InstagramCommentReplyResult,
    InstagramConnectionId,
    InstagramPrivateCommentReplyRequest,
    InstagramPrivateCommentReplyResult,
)


class InstagramPublicCommentReplier(Protocol):
    """Publishes public comment replies through an explicit connection."""

    async def reply_publicly(
        self,
        connection_id: InstagramConnectionId,
        comment_id: InstagramCommentId,
        text: str,
    ) -> InstagramCommentReplyResult:
        """Publish a public reply."""
        ...


class InstagramPrivateCommentReplier(Protocol):
    """Publishes private comment replies through an explicit connection."""

    async def reply_privately(
        self,
        connection_id: InstagramConnectionId,
        request: InstagramPrivateCommentReplyRequest,
    ) -> InstagramPrivateCommentReplyResult:
        """Publish an eligible private reply."""
        ...


class InstagramCommentReplier(
    InstagramPublicCommentReplier,
    InstagramPrivateCommentReplier,
    Protocol,
):
    """Composite reply contract for hosts that need both reply modes."""
