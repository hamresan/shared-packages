"""Start OAuth reauthorization for one explicitly selected connection."""

from instagram_auth.application.authorization.models import (
    InstagramAuthorizationCorrelation,
    InstagramAuthorizationFlow,
    InstagramAuthorizationStartResult,
    StartInstagramAuthorizationCommand,
)
from instagram_auth.application.authorization.start import StartInstagramAuthorization
from instagram_auth.application.connections.get_connection import GetInstagramConnection
from instagram_auth.domain import InstagramConnectionId


class StartInstagramConnectionReauthorization:
    """Validate ownership and create OAuth state bound to one connection."""

    def __init__(
        self,
        *,
        get_connection: GetInstagramConnection,
        start_authorization: StartInstagramAuthorization,
    ) -> None:
        self._get_connection = get_connection
        self._start_authorization = start_authorization

    async def execute(
        self,
        *,
        owner_user_id: str,
        connection_id: InstagramConnectionId,
        redirect_uri: str,
    ) -> InstagramAuthorizationStartResult:
        await self._get_connection.execute(
            owner_user_id=owner_user_id,
            connection_id=connection_id,
        )
        return await self._start_authorization.execute(
            StartInstagramAuthorizationCommand(
                redirect_uri=redirect_uri,
                correlation=InstagramAuthorizationCorrelation(
                    flow=InstagramAuthorizationFlow.RECONNECT_ACCOUNT,
                    owner_user_id=owner_user_id,
                    connection_id=str(connection_id.value),
                ),
            )
        )
