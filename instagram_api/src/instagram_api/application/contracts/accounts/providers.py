"""Provider boundary for Instagram account profile data."""

from typing import Protocol

from instagram_api.domain import InstagramAccount, InstagramConnectionId


class InstagramAccountProvider(Protocol):
    """Reads provider account data for one explicit connection."""

    async def get_account(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramAccount:
        """Return normalized provider account data for the selected connection."""
        ...
