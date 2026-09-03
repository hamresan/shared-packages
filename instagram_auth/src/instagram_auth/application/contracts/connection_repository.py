"""Instagram connection persistence contract."""

from typing import Protocol

from instagram_auth.domain import InstagramConnection, InstagramConnectionId


class InstagramConnectionRepository(Protocol):
    """Persistence boundary for independent Instagram connection records."""

    async def add(self, connection: InstagramConnection) -> None:
        """Persist a new connection."""
        ...

    async def update(self, connection: InstagramConnection) -> None:
        """Persist changes to an existing connection."""
        ...

    async def find_by_owner_and_account(
        self,
        *,
        owner_user_id: str,
        instagram_account_id: str,
    ) -> InstagramConnection | None:
        """Find a connection by host owner and opaque Instagram account identifier."""
        ...

    async def get_by_id(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramConnection | None:
        """Read a connection by its package-owned identifier."""
        ...
