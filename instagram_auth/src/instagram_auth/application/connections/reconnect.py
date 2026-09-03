"""Prepare one explicitly selected Instagram connection for reauthorization."""

from dataclasses import replace

from instagram_auth.application.contracts import InstagramAuthUnitOfWork
from instagram_auth.application.errors.connection_access import InstagramConnectionNotFoundError
from instagram_auth.baseline import InstagramConnectionState
from instagram_auth.domain import InstagramConnection, InstagramConnectionId

from .policy import InstagramConnectionOwnershipPolicy


class ReconnectInstagramConnection:
    """Mark one owned connection as authorizing without creating a new connection."""

    def __init__(
        self,
        unit_of_work: InstagramAuthUnitOfWork,
        ownership_policy: InstagramConnectionOwnershipPolicy,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._ownership_policy = ownership_policy

    async def execute(
        self,
        *,
        owner_user_id: str,
        connection_id: InstagramConnectionId,
    ) -> InstagramConnection:
        async with self._unit_of_work:
            connection = await self._unit_of_work.connections.get_by_id(connection_id)
            if connection is None:
                raise InstagramConnectionNotFoundError("Instagram connection not found")
            self._ownership_policy.ensure_owner(
                owner_user_id=owner_user_id,
                connection=connection,
            )
            reconnecting = replace(connection, status=InstagramConnectionState.AUTHORIZING)
            await self._unit_of_work.connections.update(reconnecting)
            await self._unit_of_work.commit()
        return reconnecting
