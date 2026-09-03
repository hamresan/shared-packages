"""Narrow Instagram connection read contract."""

from typing import Protocol

from instagram_auth.domain import InstagramConnection, InstagramConnectionId


class InstagramConnectionReader(Protocol):
    """Read one explicitly selected Instagram connection."""

    async def get(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramConnection | None:
        """Return the selected connection when it exists."""
        ...
