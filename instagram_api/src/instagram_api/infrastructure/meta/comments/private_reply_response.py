"""Parses Meta private comment reply responses."""

from collections.abc import Mapping

from instagram_api.domain import (
    InstagramMessageId,
    InstagramPrivateCommentReplyResult,
    InstagramUserId,
)
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError


class MetaInstagramPrivateReplyResponseParser:
    """Parses successful private-reply Send API responses."""

    def parse(
        self,
        payload: Mapping[str, object],
    ) -> InstagramPrivateCommentReplyResult:
        """Return normalized message and recipient identifiers."""

        message_id = payload.get("message_id")
        if not isinstance(message_id, str) or not message_id:
            raise MetaInvalidResponseError(
                message="Meta private reply response is missing a valid message_id.",
                status_code=200,
            )

        recipient_id = payload.get("recipient_id")
        normalized_recipient_id = (
            InstagramUserId(recipient_id)
            if isinstance(recipient_id, str) and recipient_id
            else None
        )
        return InstagramPrivateCommentReplyResult(
            message_id=InstagramMessageId(message_id),
            recipient_id=normalized_recipient_id,
        )
