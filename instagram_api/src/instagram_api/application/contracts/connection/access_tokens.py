"""Access-token boundary supplied by the host application."""

from typing import Protocol

from instagram_api.domain.identifiers import InstagramConnectionId


class InstagramAccessTokenProvider(Protocol):
    """Provides an access token for one explicit Instagram connection."""

    async def get_access_token(self, connection_id: InstagramConnectionId) -> str:
        """Return the access token for the requested connection."""
        ...
