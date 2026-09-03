"""List Instagram connections owned by one host user."""

from instagram_auth.application.contracts import InstagramConnectionLister
from instagram_auth.domain import InstagramConnection


class ListInstagramConnections:
    """Return all independent Instagram connections for one explicit owner."""

    def __init__(self, lister: InstagramConnectionLister) -> None:
        self._lister = lister

    async def execute(self, *, owner_user_id: str) -> tuple[InstagramConnection, ...]:
        return await self._lister.list_for_owner(owner_user_id)
