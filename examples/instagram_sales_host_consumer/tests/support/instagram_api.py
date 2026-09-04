"""Provider-boundary fakes for hamresan-instagram-api integration tests."""

from datetime import UTC, datetime

from instagram_api.application.contracts import (
    InstagramAccountProvider,
    InstagramMediaProvider,
    InstagramMessageRecipientEligibilityChecker,
    InstagramOutboundMessageProvider,
    InstagramPublicCommentReplyProvider,
)
from instagram_api.domain import (
    InstagramAccount,
    InstagramCommentId,
    InstagramCommentReplyResult,
    InstagramConnectionId,
    InstagramMedia,
    InstagramMediaId,
    InstagramMediaType,
    InstagramMessageId,
    InstagramMessageSendRequest,
    InstagramMessageSendResult,
    InstagramUserId,
    Page,
    PaginationCursor,
)


class FakeAccountProvider(InstagramAccountProvider):
    """Returns connection-specific account profiles."""

    def __init__(
        self,
        accounts: dict[InstagramConnectionId, InstagramAccount],
    ) -> None:
        self._accounts = accounts

    async def get_account(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramAccount:
        return self._accounts[connection_id]


class FakeMediaProvider(InstagramMediaProvider):
    """Returns connection-specific media pages."""

    def __init__(
        self,
        media: dict[InstagramConnectionId, tuple[InstagramMedia, ...]],
    ) -> None:
        self._media = media

    async def list_media(
        self,
        connection_id: InstagramConnectionId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramMedia]:
        del cursor
        return Page(items=self._media[connection_id])

    async def get_media(
        self,
        connection_id: InstagramConnectionId,
        media_id: InstagramMediaId,
    ) -> InstagramMedia:
        return next(
            media
            for media in self._media[connection_id]
            if media.id == media_id
        )


class RecordingMessageProvider(
    InstagramMessageRecipientEligibilityChecker,
    InstagramOutboundMessageProvider,
):
    """Records API-service message sends with their explicit connection."""

    def __init__(self) -> None:
        self.sent: list[
            tuple[InstagramConnectionId, InstagramMessageSendRequest]
        ] = []

    async def is_eligible(
        self,
        connection_id: InstagramConnectionId,
        recipient_id: InstagramUserId,
    ) -> bool:
        del connection_id, recipient_id
        return True

    async def send_message(
        self,
        connection_id: InstagramConnectionId,
        request: InstagramMessageSendRequest,
    ) -> InstagramMessageSendResult:
        self.sent.append((connection_id, request))
        return InstagramMessageSendResult(
            message_id=InstagramMessageId(f"reply-{len(self.sent)}"),
            recipient_id=request.recipient_id,
            correlation_id=request.correlation_id,
        )


class RecordingCommentReplyProvider(InstagramPublicCommentReplyProvider):
    """Records public comment replies with the explicit connection."""

    def __init__(self) -> None:
        self.replies: list[tuple[InstagramConnectionId, InstagramCommentId, str]] = []

    async def reply(
        self,
        connection_id: InstagramConnectionId,
        comment_id: InstagramCommentId,
        text: str,
    ) -> InstagramCommentReplyResult:
        self.replies.append((connection_id, comment_id, text))
        return InstagramCommentReplyResult(
            comment_id=InstagramCommentId(f"reply-{len(self.replies)}")
        )


def build_media(media_id: str, caption: str) -> InstagramMedia:
    """Build deterministic normalized media for integration tests."""

    return InstagramMedia(
        id=InstagramMediaId(media_id),
        media_type=InstagramMediaType.IMAGE,
        timestamp=datetime(2026, 9, 4, 12, 0, tzinfo=UTC),
        caption=caption,
    )
