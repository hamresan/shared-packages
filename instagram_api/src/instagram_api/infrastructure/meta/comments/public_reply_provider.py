"""Meta public comment reply provider."""

from instagram_api.application.comments.reply_errors import InstagramPublicReplyRejectedError
from instagram_api.application.contracts.comments import InstagramPublicCommentReplyProvider
from instagram_api.domain import (
    InstagramCommentId,
    InstagramCommentReplyResult,
    InstagramConnectionId,
)
from instagram_api.infrastructure.meta.http import (
    MetaHttpMethod,
    MetaJsonExecutor,
    MetaProviderError,
)
from instagram_api.infrastructure.meta.http.errors import MetaInvalidResponseError


class MetaInstagramPublicCommentReplyProvider(InstagramPublicCommentReplyProvider):
    """Publishes public replies through Meta's comment replies edge."""

    def __init__(self, executor: MetaJsonExecutor) -> None:
        self._executor = executor

    async def reply(
        self,
        connection_id: InstagramConnectionId,
        comment_id: InstagramCommentId,
        text: str,
    ) -> InstagramCommentReplyResult:
        try:
            payload = await self._executor.execute_json(
                connection_id=connection_id,
                method=MetaHttpMethod.POST,
                path=f"{comment_id}/replies",
                json_body={"message": text},
            )
        except MetaProviderError as exc:
            if exc.status_code == 400:
                raise InstagramPublicReplyRejectedError(exc.message) from exc
            raise

        reply_id = payload.get("id")
        if not isinstance(reply_id, str) or not reply_id:
            raise MetaInvalidResponseError(
                message="Meta public reply response is missing a valid reply id.",
                status_code=200,
            )
        return InstagramCommentReplyResult(InstagramCommentId(reply_id))
