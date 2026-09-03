"""Narrow Instagram connection listing contract."""

from typing import Protocol

from instagram_auth.domain import InstagramConnection


class InstagramConnectionLister(Protocol):
    """List all independent Instagram connections for one host owner."""

    async def list_for_owner(self, owner_user_id: str) -> tuple[InstagramConnection, ...]:
        """Return the owner's connections without selecting an implicit active connection."""
        ...
