"""Authorized Instagram access-token lookup boundary."""

from collections.abc import Collection
from typing import Protocol

from instagram_auth.baseline import InstagramPermission
from instagram_auth.domain import InstagramConnectionId


class InstagramAccessTokenProvider(Protocol):
    """Provide authorized provider access for one explicit Instagram connection."""

    async def get_access_token(
        self,
        *,
        connection_id: InstagramConnectionId,
        required_permissions: Collection[InstagramPermission] = (),
    ) -> str:
        """Return the raw provider token when the selected connection is usable."""
        ...
