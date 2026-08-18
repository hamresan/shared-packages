from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from identity import (
    AccessTokenAuthenticator,
    AccessTokenIssuer,
    AuthenticatedPrincipal,
    IssuedAccessToken,
)
from store import AuthenticatedActor

bearer = HTTPBearer(auto_error=False)
BearerCredentials = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]


class InMemoryAccessTokenAdapter(AccessTokenIssuer, AccessTokenAuthenticator):
    def __init__(self) -> None:
        self._principals: dict[str, AuthenticatedPrincipal] = {}

    async def issue(self, user_id: UUID, session_id: UUID) -> IssuedAccessToken:
        issued_at = datetime.now(UTC)
        expires_at = issued_at + timedelta(minutes=15)
        token = f"access-{uuid4()}"
        self._principals[token] = AuthenticatedPrincipal(
            user_id=user_id,
            session_id=session_id,
            authentication_method="otp",
            issued_at=issued_at,
            expires_at=expires_at,
        )
        return IssuedAccessToken(token=token, expires_at=expires_at)

    async def authenticate(self, access_token: str) -> AuthenticatedPrincipal:
        principal = self._principals.get(access_token)
        if principal is None:
            raise ValueError("Invalid access token")
        return principal


class IdentityStoreActorDependency:
    def __init__(self, authenticator: AccessTokenAuthenticator) -> None:
        self._authenticator = authenticator

    async def __call__(self, credentials: BearerCredentials) -> AuthenticatedActor:
        if credentials is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
        try:
            principal = await self._authenticator.authenticate(credentials.credentials)
        except Exception as exc:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "Invalid authentication credentials",
            ) from exc
        return AuthenticatedActor(user_id=principal.user_id)
