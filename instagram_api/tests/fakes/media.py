"""Media reader fake."""

from instagram_api.application.contracts.media import InstagramMediaReader
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
