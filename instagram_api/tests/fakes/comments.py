"""Comment contract fakes."""

from instagram_api.application.contracts.comments import (
    InstagramCommentReader,
    InstagramCommentReplier,
)
from instagram_api.domain import (
    InstagramComment,
    InstagramCommentId,
    InstagramCommentReplyResult,
    InstagramConnectionId,
    InstagramMediaId,
    Page,
    PaginationCursor,
)


class FakeInstagramCommentReader(InstagramCommentReader):
    """Fake comment reader isolated by connection and target."""

    def __init__(
        self,
        comments: dict[
            tuple[InstagramConnectionId, InstagramMediaId],
            tuple[InstagramComment, ...],
        ],
        replies: dict[
            tuple[InstagramConnectionId, InstagramCommentId],
            tuple[InstagramComment, ...],
        ],
    ) -> None:
        self._comments = comments
        self._replies = replies

    async def list_comments(
        self,
        connection_id: InstagramConnectionId,
        media_id: InstagramMediaId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramComment]:
        del cursor
        return Page(items=self._comments[(connection_id, media_id)])

    async def list_replies(
        self,
        connection_id: InstagramConnectionId,
        comment_id: InstagramCommentId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramComment]:
        del cursor
        return Page(items=self._replies[(connection_id, comment_id)])


class FakeInstagramCommentReplier(InstagramCommentReplier):
    """Fake replier that records connection-aware reply operations."""

    def __init__(self) -> None:
        self.public_replies: list[tuple[InstagramConnectionId, InstagramCommentId, str]] = []
        self.private_replies: list[tuple[InstagramConnectionId, InstagramCommentId, str]] = []

    async def reply_publicly(
        self,
        connection_id: InstagramConnectionId,
        comment_id: InstagramCommentId,
        text: str,
    ) -> InstagramCommentReplyResult:
        self.public_replies.append((connection_id, comment_id, text))
        return InstagramCommentReplyResult(InstagramCommentId("public-reply"))

    async def reply_privately(
        self,
        connection_id: InstagramConnectionId,
        comment_id: InstagramCommentId,
        text: str,
    ) -> InstagramCommentReplyResult:
        self.private_replies.append((connection_id, comment_id, text))
        return InstagramCommentReplyResult(InstagramCommentId("private-reply"))
