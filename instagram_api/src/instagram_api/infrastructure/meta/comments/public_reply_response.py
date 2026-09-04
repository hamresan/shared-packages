"""Parses Meta public comment reply responses."""

from collections.abc import Mapping

from instagram_api.domain import InstagramCommentId, InstagramCommentReplyResult
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError


class MetaInstagramPublicReplyResponseParser:
    """Parses successful public reply responses."""

    def parse(self, payload: Mapping[str, object]) -> InstagramCommentReplyResult:
        """Return the created public reply identifier."""

        reply_id = payload.get("id")
        if not isinstance(reply_id, str) or not reply_id:
            raise MetaInvalidResponseError(
                message="Meta public reply response is missing a valid reply id.",
                status_code=200,
            )
        return InstagramCommentReplyResult(InstagramCommentId(reply_id))
