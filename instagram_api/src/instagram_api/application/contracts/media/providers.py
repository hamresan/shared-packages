"""Provider boundary for Instagram media data."""

from typing import Protocol

from instagram_api.domain import (
    InstagramConnectionId,
    InstagramMedia,
    InstagramMediaId,
    Page,
    PaginationCursor,
)


class InstagramMediaProvider(Protocol):
    """Reads normalized media for one explicit Instagram connection."""

    async def list_media(
        self,
        connection_id: InstagramConnectionId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramMedia]:
        """Return one page of owned media for the selected connection."""
        ...

    async def get_media(
        self,
        connection_id: InstagramConnectionId,
        media_id: InstagramMediaId,
    ) -> InstagramMedia:
        """Return one media item for the selected connection."""
        ...
