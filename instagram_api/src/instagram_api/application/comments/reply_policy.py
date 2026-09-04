"""Policies for Instagram public and private comment replies."""

from datetime import timedelta

from instagram_api.domain import (
    InstagramConnection,
    InstagramPrivateCommentReplyRequest,
    InstagramPrivateReplySource,
)

from .errors import (
    InstagramCommentConnectionUnavailableError,
    InstagramCommentPermissionRequiredError,
)
from .reply_clock import InstagramReplyClock
from .reply_errors import (
    InstagramCommentReplyPayloadInvalidError,
    InstagramPrivateReplyExpiredError,
    InstagramPrivateReplyLiveInactiveError,
)

INSTAGRAM_COMMENT_REPLY_BASIC_PERMISSION = "instagram_business_basic"
INSTAGRAM_COMMENT_REPLY_MANAGE_PERMISSION = "instagram_business_manage_comments"
PRIVATE_REPLY_WINDOW = timedelta(days=7)


class InstagramLiveCommentCapabilityPolicy:
    """Exposes verified Live-comment capability constraints."""

    def can_normalize_webhook(self) -> bool:
        """Return whether documented Live comment webhooks are supported."""

        return True

    def can_reply_privately(self, live_is_active: bool | None) -> bool:
        """Return whether a Live private reply is currently eligible."""

        return live_is_active is True

    def can_discover_active_session(self) -> bool:
        """Return whether active Live session discovery is verified."""

        return False

    def can_read_historical_comments(self) -> bool:
        """Return whether historical Live comment retrieval is verified."""

        return False

    def can_read_live_stream(self) -> bool:
        """Return whether raw Live video/audio ingestion is supported."""

        return False


class InstagramCommentReplyAccessPolicy:
    """Validates connection permissions for comment reply operations."""

    def validate_connection(self, connection: InstagramConnection) -> None:
        """Require a usable connection with comment-management permissions."""

        if not connection.is_usable:
            raise InstagramCommentConnectionUnavailableError(
                "Selected Instagram connection is not usable."
            )

        required_permissions = {
            INSTAGRAM_COMMENT_REPLY_BASIC_PERMISSION,
            INSTAGRAM_COMMENT_REPLY_MANAGE_PERMISSION,
        }
        missing_permissions = required_permissions.difference(connection.permissions)
        if missing_permissions:
            permission = sorted(missing_permissions)[0]
            raise InstagramCommentPermissionRequiredError(
                f"Required permission is missing: {permission}"
            )


class InstagramCommentReplyTextPolicy:
    """Validates reply text shared by public and private use cases."""

    def validate(self, text: str) -> None:
        """Reject blank reply text."""

        if not text.strip():
            raise InstagramCommentReplyPayloadInvalidError("Comment reply text must not be blank.")


class InstagramPrivateReplyEligibilityPolicy:
    """Applies Meta's documented private-reply timing constraints."""

    def __init__(self, clock: InstagramReplyClock) -> None:
        self._clock = clock

    def validate(self, request: InstagramPrivateCommentReplyRequest) -> None:
        """Validate standard and Live private-reply timing separately."""

        if request.source is InstagramPrivateReplySource.LIVE:
            if request.live_is_active is not True:
                raise InstagramPrivateReplyLiveInactiveError(
                    "Instagram Live private replies require an active broadcast."
                )
            return

        now = self._clock.now()
        if request.comment_created_at > now:
            raise InstagramPrivateReplyExpiredError(
                "Comment creation time cannot be in the future."
            )

        if now - request.comment_created_at > PRIVATE_REPLY_WINDOW:
            raise InstagramPrivateReplyExpiredError("Private reply window has expired.")
