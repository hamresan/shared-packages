"""Meta Send API provider for outbound Instagram messages."""

import logging

from instagram_api.application.contracts.messaging import InstagramOutboundMessageProvider
from instagram_api.domain import (
    InstagramConnectionId,
    InstagramMessageSendRequest,
    InstagramMessageSendResult,
)
from instagram_api.infrastructure.meta.http import (
    MetaHttpMethod,
    MetaJsonExecutor,
    MetaProviderError,
)

from .outbound_error_mapper import MetaInstagramMessageSendErrorMapper
from .outbound_payload import MetaInstagramOutboundPayloadMapper
from .outbound_response import MetaInstagramMessageSendResponseParser

logger = logging.getLogger(__name__)


class MetaInstagramOutboundMessageProvider(InstagramOutboundMessageProvider):
    """Sends supported messages through Meta's non-idempotent Send API."""

    def __init__(
        self,
        executor: MetaJsonExecutor,
        payload_mapper: MetaInstagramOutboundPayloadMapper,
        response_parser: MetaInstagramMessageSendResponseParser,
        error_mapper: MetaInstagramMessageSendErrorMapper,
    ) -> None:
        self._executor = executor
        self._payload_mapper = payload_mapper
        self._response_parser = response_parser
        self._error_mapper = error_mapper

    async def send_message(
        self,
        connection_id: InstagramConnectionId,
        request: InstagramMessageSendRequest,
    ) -> InstagramMessageSendResult:
        provider_payload = self._payload_mapper.to_provider(request)
        message = provider_payload.get("message", {})
        quick_replies = message.get("quick_replies", [])
        logger.info(
            "Instagram outbound payload diagnostics: has_text=%s quick_reply_count=%d "
            "quick_reply_titles=%s message_keys=%s",
            bool(message.get("text")),
            len(quick_replies),
            [reply.get("title") for reply in quick_replies],
            sorted(message.keys()),
        )

        try:
            payload = await self._executor.execute_json(
                connection_id=connection_id,
                method=MetaHttpMethod.POST,
                path="me/messages",
                json_body=provider_payload,
            )
        except MetaProviderError as exc:
            raise self._error_mapper.map(exc) from exc

        return InstagramMessageSendResult(
            message_id=self._response_parser.message_id(payload),
            recipient_id=self._response_parser.recipient_id(payload),
        )
