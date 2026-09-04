"""Instagram comment reading application service."""

from instagram_api.application.contracts.comments import (
    InstagramCommentProvider,
    InstagramCommentReader,
)
from instagram_api.application.contracts.connection import InstagramConnectionReader
from instagram_api.domain import (
    InstagramComment,
    InstagramCommentId,
    InstagramConnectionId,
    InstagramMediaId,
    Page,
    PaginationCursor,
)

from .policy import InstagramCommentAccessPolicy


class InstagramCommentService(InstagramCommentReader):
    """Reads comments through one explicitly selected Instagram connection."""

    def __init__(
        self,
        connection_reader: InstagramConnectionReader,
        comment_provider: InstagramCommentProvider,
        access_policy: InstagramCommentAccessPolicy,
    ) -> None:
        self._connection_reader = connection_reader
        self._comment_provider = comment_provider
        self._access_policy = access_policy

    async def list_comments(
        self,
        connection_id: InstagramConnectionId,
        media_id: InstagramMediaId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramComment]:
        connection = await self._connection_reader.get_connection(connection_id)
        self._access_policy.validate_connection(connection)
        return await self._comment_provider.list_comments(connection_id, media_id, cursor)

    async def list_replies(
        self,
        connection_id: InstagramConnectionId,
        comment_id: InstagramCommentId,
        cursor: PaginationCursor | None = None,
    ) -> Page[InstagramComment]:
        connection = await self._connection_reader.get_connection(connection_id)
        self._access_policy.validate_connection(connection)
        return await self._comment_provider.list_replies(
            connection_id,
            comment_id,
            cursor,
        )
