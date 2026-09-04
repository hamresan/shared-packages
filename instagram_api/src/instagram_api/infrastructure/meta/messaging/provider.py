"""Meta provider implementations for Instagram conversation and message reads."""

from instagram_api.application.contracts.messaging import (
    InstagramConversationProvider,
    InstagramMessageProvider,
)
from instagram_api.domain import (
    InstagramConnectionId,
    InstagramConversation,
    InstagramConversationId,
    InstagramMessage,
    InstagramMessageId,
    Page,
    PaginationCursor,
)
from instagram_api.infrastructure.meta.http import (
    MetaHttpMethod,
    MetaJsonExecutor,
    MetaPaginationCursorMapper,
    MetaProviderError,
)

from .detail_policy import MetaInstagramMessageDetailAvailabilityPolicy
from .dto import MetaInstagramMessageDetailDto, MetaInstagramMessageSummaryDto
from .mapper import MetaInstagramMessagingMapper
from .parser import MetaInstagramMessagingPayloadParser
from .query_builder import MetaInstagramMessageQueryBuilder

MESSAGE_DETAIL_FIELDS = "id,created_time,from,to,message"


class MetaInstagramConversationProvider(InstagramConversationProvider):
    """Lists Instagram conversations for one explicit connection."""

    def __init__(
        self,
        executor: MetaJsonExecutor,
        parser: MetaInstagramMessagingPayloadParser,
        mapper: MetaInstagramMessagingMapper,
        pagination_mapper: MetaPaginationCursorMapper,
    ) -> None:
        self._executor = executor
        self._parser = parser
        self._mapper = mapper
        self._pagination_mapper = pagination_mapper

    async def list_conversations(
        self,
        connection_id: InstagramConnectionId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramConversation]:
        params = {"platform": "instagram"}
        if cursor is not None:
            params["after"] = cursor

        payload = await self._executor.execute_json(
            connection_id=connection_id,
            method=MetaHttpMethod.GET,
            path="me/conversations",
            params=params,
        )
        dtos = self._parser.parse_conversations(payload)
        return Page(
            items=tuple(self._mapper.conversation(dto) for dto in dtos),
            next_cursor=self._pagination_mapper.next_cursor(payload),
        )


class MetaInstagramMessageProvider(InstagramMessageProvider):
    """Lists messages and enriches recent supported messages with details."""

    def __init__(
        self,
        executor: MetaJsonExecutor,
        parser: MetaInstagramMessagingPayloadParser,
        mapper: MetaInstagramMessagingMapper,
        pagination_mapper: MetaPaginationCursorMapper,
        query_builder: MetaInstagramMessageQueryBuilder,
        detail_policy: MetaInstagramMessageDetailAvailabilityPolicy,
    ) -> None:
        self._executor = executor
        self._parser = parser
        self._mapper = mapper
        self._pagination_mapper = pagination_mapper
        self._query_builder = query_builder
        self._detail_policy = detail_policy

    async def list_messages(
        self,
        connection_id: InstagramConnectionId,
        conversation_id: InstagramConversationId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramMessage]:
        payload = await self._executor.execute_json(
            connection_id=connection_id,
            method=MetaHttpMethod.GET,
            path=str(conversation_id),
            params={"fields": self._query_builder.fields(cursor)},
        )
        summaries = self._parser.parse_message_summaries(payload)
        messages: list[InstagramMessage] = []

        for summary in summaries:
            detail = await self._read_detail(connection_id, summary)
            messages.append(self._mapper.message(conversation_id, summary, detail))

        messages_payload = self._parser.messages_container(payload)
        return Page(
            items=tuple(messages),
            next_cursor=self._pagination_mapper.next_cursor(messages_payload),
        )

    async def _read_detail(
        self,
        connection_id: InstagramConnectionId,
        summary: MetaInstagramMessageSummaryDto,
    ) -> MetaInstagramMessageDetailDto | None:
        if summary.is_unsupported:
            return None

        try:
            payload = await self._executor.execute_json(
                connection_id=connection_id,
                method=MetaHttpMethod.GET,
                path=str(InstagramMessageId(summary.id)),
                params={"fields": MESSAGE_DETAIL_FIELDS},
            )
        except MetaProviderError as exc:
            if self._detail_policy.details_are_unavailable(exc):
                return None
            raise

        return self._parser.parse_message_detail(payload)
