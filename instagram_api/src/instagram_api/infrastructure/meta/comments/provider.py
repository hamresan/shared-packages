"""Meta provider implementation for Instagram comment reads."""

from instagram_api.application.contracts.comments import InstagramCommentProvider
from instagram_api.domain import (
    InstagramComment,
    InstagramCommentId,
    InstagramConnectionId,
    InstagramMediaId,
    Page,
    PaginationCursor,
)
from instagram_api.infrastructure.meta.http import (
    MetaHttpMethod,
    MetaJsonExecutor,
    MetaPaginationCursorMapper,
)

from .mapper import MetaInstagramCommentMapper
from .parser import MetaInstagramCommentPayloadParser

COMMENT_FIELDS = (
    "id",
    "text",
    "timestamp",
    "from{id}",
    "media{id}",
    "parent_id{id}",
)


class MetaInstagramCommentProvider(InstagramCommentProvider):
    """Reads comments and replies through the shared Meta HTTP foundation."""

    def __init__(
        self,
        executor: MetaJsonExecutor,
        parser: MetaInstagramCommentPayloadParser,
        mapper: MetaInstagramCommentMapper,
        pagination_mapper: MetaPaginationCursorMapper,
    ) -> None:
        self._executor = executor
        self._parser = parser
        self._mapper = mapper
        self._pagination_mapper = pagination_mapper

    async def list_comments(
        self,
        connection_id: InstagramConnectionId,
        media_id: InstagramMediaId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramComment]:
        params: dict[str, str] = {"fields": ",".join(COMMENT_FIELDS)}
        if cursor is not None:
            params["after"] = cursor

        payload = await self._executor.execute_json(
            connection_id=connection_id,
            method=MetaHttpMethod.GET,
            path=f"{media_id}/comments",
            params=params,
        )
        dtos = self._parser.parse_collection(
            payload,
            fallback_media_id=str(media_id),
        )
        return Page(
            items=tuple(self._mapper.to_domain(dto) for dto in dtos),
            next_cursor=self._pagination_mapper.next_cursor(payload),
        )

    async def list_replies(
        self,
        connection_id: InstagramConnectionId,
        comment_id: InstagramCommentId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramComment]:
        params: dict[str, str] = {"fields": ",".join(COMMENT_FIELDS)}
        if cursor is not None:
            params["after"] = cursor

        payload = await self._executor.execute_json(
            connection_id=connection_id,
            method=MetaHttpMethod.GET,
            path=f"{comment_id}/replies",
            params=params,
        )
        dtos = self._parser.parse_collection(
            payload,
            fallback_parent_id=str(comment_id),
        )
        return Page(
            items=tuple(self._mapper.to_domain(dto) for dto in dtos),
            next_cursor=self._pagination_mapper.next_cursor(payload),
        )
