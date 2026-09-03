"""Read one Instagram connection with host ownership enforcement."""

from instagram_auth.application.contracts import InstagramConnectionReader
from instagram_auth.application.errors.connection_access import InstagramConnectionNotFoundError
from instagram_auth.domain import InstagramConnection, InstagramConnectionId

from .policy import InstagramConnectionOwnershipPolicy


class GetInstagramConnection:
    """Read one explicit connection after validating host ownership."""

    def __init__(
        self,
        reader: InstagramConnectionReader,
        ownership_policy: InstagramConnectionOwnershipPolicy,
    ) -> None:
        self._reader = reader
        self._ownership_policy = ownership_policy

    async def execute(
        self,
        *,
        owner_user_id: str,
        connection_id: InstagramConnectionId,
    ) -> InstagramConnection:
        connection = await self._reader.get(connection_id)
        if connection is None:
            raise InstagramConnectionNotFoundError("Instagram connection not found")
        self._ownership_policy.ensure_owner(
            owner_user_id=owner_user_id,
            connection=connection,
        )
        return connection
