"""Connection-reading boundary supplied by the host application."""

from typing import Protocol

from instagram_api.domain.connections import InstagramConnection
from instagram_api.domain.identifiers import InstagramConnectionId


class InstagramConnectionReader(Protocol):
    """Reads one explicit Instagram connection without persistence coupling."""

    async def get_connection(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramConnection:
        """Return the requested connection."""
        ...
