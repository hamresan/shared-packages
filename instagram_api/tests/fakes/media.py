"""Media reader and provider fakes."""

from instagram_api.application.contracts.media import InstagramMediaProvider, InstagramMediaReader
from instagram_api.domain import (
    InstagramConnectionId,
    InstagramMedia,
    InstagramMediaId,
    Page,
    PaginationCursor,
)


class FakeInstagramMediaReader(InstagramMediaReader):
    """Fake media reader isolated by connection ID."""

    def __init__(
        self,
        media_by_connection: dict[InstagramConnectionId, tuple[InstagramMedia, ...]],
    ) -> None:
        self._media_by_connection = media_by_connection

    async def list_media(
        self,
        connection_id: InstagramConnectionId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramMedia]:
        del cursor
        return Page(items=self._media_by_connection[connection_id])

    async def get_media(
        self,
        connection_id: InstagramConnectionId,
        media_id: InstagramMediaId,
    ) -> InstagramMedia:
        for media in self._media_by_connection[connection_id]:
            if media.id == media_id:
                return media
        raise KeyError(media_id)


class FakeInstagramMediaProvider(InstagramMediaProvider):
    """Fake media provider isolated by explicit connection ID."""

    def __init__(
        self,
        pages: dict[InstagramConnectionId, Page[InstagramMedia]],
    ) -> None:
        self._pages = pages
        self.list_calls: list[tuple[InstagramConnectionId, PaginationCursor | None]] = []
        self.get_calls: list[tuple[InstagramConnectionId, InstagramMediaId]] = []

    async def list_media(
        self,
        connection_id: InstagramConnectionId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramMedia]:
        self.list_calls.append((connection_id, cursor))
        return self._pages[connection_id]

    async def get_media(
        self,
        connection_id: InstagramConnectionId,
        media_id: InstagramMediaId,
    ) -> InstagramMedia:
        self.get_calls.append((connection_id, media_id))
        for media in self._pages[connection_id].items:
            if media.id == media_id:
                return media
        raise KeyError(media_id)
