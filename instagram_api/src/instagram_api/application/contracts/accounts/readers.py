"""Instagram account reading contracts."""

from typing import Protocol

from instagram_api.domain.accounts import InstagramAccount
from instagram_api.domain.identifiers import InstagramConnectionId


class InstagramAccountReader(Protocol):
    """Reads the account profile for one explicit connection."""

    async def get_account(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramAccount:
        """Return the account attached to the requested connection."""
        ...
