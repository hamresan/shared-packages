"""Meta public comment reply provider."""

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

from .public_reply_error_mapper import MetaInstagramPublicReplyErrorMapper
from .public_reply_response import MetaInstagramPublicReplyResponseParser


class MetaInstagramPublicCommentReplyProvider(InstagramPublicCommentReplyProvider):
    """Publishes public replies through Meta's comment replies edge."""

    def __init__(
        self,
        executor: MetaJsonExecutor,
        response_parser: MetaInstagramPublicReplyResponseParser,
        error_mapper: MetaInstagramPublicReplyErrorMapper,
    ) -> None:
        self._executor = executor
        self._response_parser = response_parser
        self._error_mapper = error_mapper

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
                params={"message": text},
            )
        except MetaProviderError as exc:
            raise self._error_mapper.map(exc) from exc

        return self._response_parser.parse(payload)
