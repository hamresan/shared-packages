"""Instagram media reading contracts."""

from typing import Protocol

from instagram_api.domain.identifiers import (
    InstagramConnectionId,
    InstagramMediaId,
    PaginationCursor,
)
from instagram_api.domain.media import InstagramMedia
from instagram_api.domain.pagination import Page


class InstagramMediaReader(Protocol):
    """Reads owned media through one explicit Instagram connection."""

    async def list_media(
        self,
        connection_id: InstagramConnectionId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramMedia]:
        """Return one page of media for the requested connection."""
        ...

    async def get_media(
        self,
        connection_id: InstagramConnectionId,
        media_id: InstagramMediaId,
    ) -> InstagramMedia:
        """Return one media item through the requested connection."""
        ...
