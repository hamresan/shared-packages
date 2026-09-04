"""Instagram media application service."""

from instagram_api.application.contracts.connection import InstagramConnectionReader
from instagram_api.application.contracts.media import InstagramMediaProvider, InstagramMediaReader
from instagram_api.domain import (
    InstagramConnectionId,
    InstagramMedia,
    InstagramMediaId,
    Page,
    PaginationCursor,
)

from .policy import InstagramMediaAccessPolicy


class InstagramMediaService(InstagramMediaReader):
    """Reads selected-connection media through explicit boundaries."""

    def __init__(
        self,
        connection_reader: InstagramConnectionReader,
        media_provider: InstagramMediaProvider,
        access_policy: InstagramMediaAccessPolicy,
    ) -> None:
        self._connection_reader = connection_reader
        self._media_provider = media_provider
        self._access_policy = access_policy

    async def list_media(
        self,
        connection_id: InstagramConnectionId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramMedia]:
        connection = await self._connection_reader.get_connection(connection_id)
        self._access_policy.validate_connection(connection)
        return await self._media_provider.list_media(connection_id, cursor)

    async def get_media(
        self,
        connection_id: InstagramConnectionId,
        media_id: InstagramMediaId,
    ) -> InstagramMedia:
        connection = await self._connection_reader.get_connection(connection_id)
        self._access_policy.validate_connection(connection)
        return await self._media_provider.get_media(connection_id, media_id)
