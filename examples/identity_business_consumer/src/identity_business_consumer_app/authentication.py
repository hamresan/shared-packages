from typing import Annotated

from business.application import AuthenticatedActor
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from identity.public import AccessTokenAuthenticationError, AccessTokenAuthenticator

bearer = HTTPBearer(auto_error=False)


class IdentityBusinessActorDependency:
    def __init__(self, authenticator: AccessTokenAuthenticator) -> None:
        self._authenticator = authenticator

    async def __call__(
        self, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]
    ) -> AuthenticatedActor:
        if credentials is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
        try:
            principal = await self._authenticator.authenticate(credentials.credentials)
        except AccessTokenAuthenticationError as exc:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid access token") from exc
        return AuthenticatedActor(principal.user_id)
