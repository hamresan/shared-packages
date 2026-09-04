"""Meta private comment reply provider."""

from instagram_api.application.contracts.comments import InstagramPrivateCommentReplyProvider
from instagram_api.domain import (
    InstagramConnectionId,
    InstagramPrivateCommentReplyRequest,
    InstagramPrivateCommentReplyResult,
)
from instagram_api.infrastructure.meta.http import (
    MetaHttpMethod,
    MetaJsonExecutor,
    MetaProviderError,
)

from .private_reply_error_mapper import MetaInstagramPrivateReplyErrorMapper
from .private_reply_payload import MetaInstagramPrivateReplyPayloadMapper
from .private_reply_response import MetaInstagramPrivateReplyResponseParser


class MetaInstagramPrivateCommentReplyProvider(InstagramPrivateCommentReplyProvider):
    """Publishes eligible private replies through Meta's Send API."""

    def __init__(
        self,
        executor: MetaJsonExecutor,
        payload_mapper: MetaInstagramPrivateReplyPayloadMapper,
        response_parser: MetaInstagramPrivateReplyResponseParser,
        error_mapper: MetaInstagramPrivateReplyErrorMapper,
    ) -> None:
        self._executor = executor
        self._payload_mapper = payload_mapper
        self._response_parser = response_parser
        self._error_mapper = error_mapper

    async def reply(
        self,
        connection_id: InstagramConnectionId,
        request: InstagramPrivateCommentReplyRequest,
    ) -> InstagramPrivateCommentReplyResult:
        try:
            payload = await self._executor.execute_json(
                connection_id=connection_id,
                method=MetaHttpMethod.POST,
                path="me/messages",
                json_body=self._payload_mapper.to_provider(request),
            )
        except MetaProviderError as exc:
            raise self._error_mapper.map(exc) from exc

        return self._response_parser.parse(payload)
