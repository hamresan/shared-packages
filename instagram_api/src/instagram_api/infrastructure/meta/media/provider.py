"""Meta provider implementation for Instagram media reads."""

from instagram_api.application.contracts.media import InstagramMediaProvider
from instagram_api.domain import (
    InstagramConnectionId,
    InstagramMedia,
    InstagramMediaId,
    Page,
    PaginationCursor,
)
from instagram_api.infrastructure.meta.http import (
    MetaHttpMethod,
    MetaJsonExecutor,
    MetaPaginationCursorMapper,
    MetaProviderError,
)

from .error_mapper import MetaInstagramMediaErrorMapper
from .mapper import MetaInstagramMediaMapper
from .parser import MetaInstagramMediaPayloadParser

MEDIA_FIELDS = (
    "id",
    "caption",
    "media_type",
    "media_product_type",
    "media_url",
    "thumbnail_url",
    "permalink",
    "timestamp",
    "children{id}",
)


class MetaInstagramMediaProvider(InstagramMediaProvider):
    """Reads owned media through the shared Meta HTTP foundation."""

    def __init__(
        self,
        executor: MetaJsonExecutor,
        parser: MetaInstagramMediaPayloadParser,
        mapper: MetaInstagramMediaMapper,
        pagination_mapper: MetaPaginationCursorMapper,
        error_mapper: MetaInstagramMediaErrorMapper,
    ) -> None:
        self._executor = executor
        self._parser = parser
        self._mapper = mapper
        self._pagination_mapper = pagination_mapper
        self._error_mapper = error_mapper

    async def list_media(
        self,
        connection_id: InstagramConnectionId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramMedia]:
        params = {"fields": ",".join(MEDIA_FIELDS)}
        if cursor is not None:
            params["after"] = cursor

        payload = await self._executor.execute_json(
            connection_id=connection_id,
            method=MetaHttpMethod.GET,
            path="me/media",
            params=params,
        )
        dtos = self._parser.parse_media_list(payload)
        return Page(
            items=tuple(self._mapper.to_domain(dto) for dto in dtos),
            next_cursor=self._pagination_mapper.next_cursor(payload),
        )

    async def get_media(
        self,
        connection_id: InstagramConnectionId,
        media_id: InstagramMediaId,
    ) -> InstagramMedia:
        try:
            payload = await self._executor.execute_json(
                connection_id=connection_id,
                method=MetaHttpMethod.GET,
                path=str(media_id),
                params={"fields": ",".join(MEDIA_FIELDS)},
            )
        except MetaProviderError as exc:
            raise self._error_mapper.map(exc) from exc

        dto = self._parser.parse_media(payload)
        return self._mapper.to_domain(dto)
