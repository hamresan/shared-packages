"""Ownership policy for connection-management use cases."""

from instagram_auth.application.errors.connection_access import (
    InstagramConnectionOwnershipError,
)
from instagram_auth.domain import InstagramConnection


class InstagramConnectionOwnershipPolicy:
    """Authorize one explicit host owner against one connection."""

    def ensure_owner(
        self,
        *,
        owner_user_id: str,
        connection: InstagramConnection,
    ) -> None:
        if connection.owner_user_id != owner_user_id:
            raise InstagramConnectionOwnershipError(
                "Instagram connection does not belong to the requested owner"
            )
