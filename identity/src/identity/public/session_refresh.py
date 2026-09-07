from identity.application.dto import AuthSessionResult, RefreshSessionCommand
from identity.application.errors import IdentityError, InvalidRefreshTokenError
from identity.public.errors import SessionRefreshError, SessionRefreshRejectedError
from identity.public.services import SessionRefresher


class PublicSessionRefresher(SessionRefresher):
    """Expose stable public refresh errors while delegating to the application service."""

    def __init__(self, delegate: SessionRefresher) -> None:
        self._delegate = delegate

    async def execute(self, command: RefreshSessionCommand) -> AuthSessionResult:
        try:
            return await self._delegate.execute(command)
        except InvalidRefreshTokenError as error:
            raise SessionRefreshRejectedError("Session refresh rejected") from error
        except IdentityError as error:
            raise SessionRefreshError("Session refresh failed") from error
