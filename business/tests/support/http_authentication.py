from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from business.application.actor import AuthenticatedActor

test_bearer = HTTPBearer(auto_error=False)


class TestAuthenticatedActorDependency:
    def __init__(self, tokens: dict[str, UUID]) -> None:
        self._tokens = tokens

    async def __call__(
        self, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(test_bearer)]
    ) -> AuthenticatedActor:
        user_id = self._tokens.get(credentials.credentials) if credentials is not None else None
        if user_id is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
        return AuthenticatedActor(user_id=user_id)
