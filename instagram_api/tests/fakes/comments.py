"""Comment contract fakes."""

from instagram_api.application.contracts.comments import (
    InstagramCommentProvider,
    InstagramCommentReader,
    InstagramCommentReplier,
    InstagramPrivateCommentReplyProvider,
    InstagramPublicCommentReplyProvider,
)
from instagram_api.domain import (
    InstagramComment,
    InstagramCommentId,
    InstagramCommentReplyResult,
    InstagramConnectionId,
    InstagramMediaId,
    InstagramMessageId,
    InstagramPrivateCommentReplyRequest,
    InstagramPrivateCommentReplyResult,
    InstagramUserId,
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
    """Fake composite replier for contract compatibility tests."""

    def __init__(self) -> None:
        self.public_replies: list[
            tuple[InstagramConnectionId, InstagramCommentId, str]
        ] = []
        self.private_replies: list[
            tuple[InstagramConnectionId, InstagramPrivateCommentReplyRequest]
        ] = []

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
        request: InstagramPrivateCommentReplyRequest,
    ) -> InstagramPrivateCommentReplyResult:
        self.private_replies.append((connection_id, request))
        return InstagramPrivateCommentReplyResult(
            message_id=InstagramMessageId("private-message"),
            recipient_id=InstagramUserId("recipient"),
        )


class FakeInstagramPublicCommentReplyProvider(InstagramPublicCommentReplyProvider):
    """Fake public reply provider that records explicit connection routing."""

    def __init__(self) -> None:
        self.calls: list[tuple[InstagramConnectionId, InstagramCommentId, str]] = []

    async def reply(
        self,
        connection_id: InstagramConnectionId,
        comment_id: InstagramCommentId,
        text: str,
    ) -> InstagramCommentReplyResult:
        self.calls.append((connection_id, comment_id, text))
        return InstagramCommentReplyResult(InstagramCommentId("public-reply"))


class FakeInstagramPrivateCommentReplyProvider(InstagramPrivateCommentReplyProvider):
    """Fake private reply provider that records explicit connection routing."""

    def __init__(self) -> None:
        self.calls: list[
            tuple[InstagramConnectionId, InstagramPrivateCommentReplyRequest]
        ] = []

    async def reply(
        self,
        connection_id: InstagramConnectionId,
        request: InstagramPrivateCommentReplyRequest,
    ) -> InstagramPrivateCommentReplyResult:
        self.calls.append((connection_id, request))
        return InstagramPrivateCommentReplyResult(
            message_id=InstagramMessageId("private-message"),
            recipient_id=InstagramUserId("recipient"),
        )


class FakeInstagramCommentProvider(InstagramCommentProvider):
    """Fake comment provider that records connection-aware reads."""

    def __init__(
        self,
        comment_pages: dict[
            tuple[InstagramConnectionId, InstagramMediaId],
            Page[InstagramComment],
        ],
        reply_pages: dict[
            tuple[InstagramConnectionId, InstagramCommentId],
            Page[InstagramComment],
        ],
    ) -> None:
        self._comment_pages = comment_pages
        self._reply_pages = reply_pages
        self.comment_calls: list[
            tuple[InstagramConnectionId, InstagramMediaId, PaginationCursor | None]
        ] = []
        self.reply_calls: list[
            tuple[InstagramConnectionId, InstagramCommentId, PaginationCursor | None]
        ] = []

    async def list_comments(
        self,
        connection_id: InstagramConnectionId,
        media_id: InstagramMediaId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramComment]:
        self.comment_calls.append((connection_id, media_id, cursor))
        return self._comment_pages[(connection_id, media_id)]

    async def list_replies(
        self,
        connection_id: InstagramConnectionId,
        comment_id: InstagramCommentId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramComment]:
        self.reply_calls.append((connection_id, comment_id, cursor))
        return self._reply_pages[(connection_id, comment_id)]
