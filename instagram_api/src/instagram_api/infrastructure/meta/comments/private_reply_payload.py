"""Maps private comment replies to Meta Send API payloads."""

from collections.abc import Mapping

from instagram_api.domain import InstagramPrivateCommentReplyRequest


class MetaInstagramPrivateReplyPayloadMapper:
    """Builds Meta private-reply JSON from normalized requests."""

    def to_provider(
        self,
        request: InstagramPrivateCommentReplyRequest,
    ) -> Mapping[str, object]:
        """Map a private reply request to Meta Send API JSON."""

        return {
            "recipient": {"comment_id": str(request.comment_id)},
            "message": {"text": request.text},
        }
