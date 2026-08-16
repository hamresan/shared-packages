from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from identity.public import AccessTokenAuthenticator, AuthenticatedPrincipal

bearer = HTTPBearer(auto_error=False)
BearerCredentials = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]


@dataclass(frozen=True, slots=True)
class FastApiIdentityAdapter:
    access_token_authenticator: AccessTokenAuthenticator

    def router(self) -> APIRouter:
        router = APIRouter(prefix="/identity", tags=["identity"])

        @router.get("/me", response_model=dict[str, str])
        async def me(
            principal: Annotated[
                AuthenticatedPrincipal,
                Depends(self.require_authenticated_user),
            ],
        ) -> dict[str, str]:
            return {
                "user_id": str(principal.user_id),
                "session_id": str(principal.session_id),
            }

        return router

    async def require_authenticated_user(
        self,
        credentials: BearerCredentials,
    ) -> AuthenticatedPrincipal:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )
        try:
            return await self.access_token_authenticator.authenticate(credentials.credentials)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            ) from exc

    def install(self, app: FastAPI) -> None:
        app.include_router(self.router())
