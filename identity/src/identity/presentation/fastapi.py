from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from identity.public import AccessTokenAuthenticator, AuthenticatedPrincipal

bearer = HTTPBearer(auto_error=False)
BearerCredentials = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]


@dataclass(frozen=True, slots=True)
class AuthenticatedUserDependency:
    access_token_authenticator: AccessTokenAuthenticator

    async def __call__(
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


@dataclass(frozen=True, slots=True)
class CurrentUserEndpoint:
    require_authenticated_user: AuthenticatedUserDependency

    async def __call__(
        self,
        principal: Annotated[
            AuthenticatedPrincipal,
            Depends(),
        ],
    ) -> dict[str, str]:
        return {
            "user_id": str(principal.user_id),
            "session_id": str(principal.session_id),
        }


@dataclass(frozen=True, slots=True)
class FastApiIdentityAdapter:
    access_token_authenticator: AccessTokenAuthenticator

    def router(self) -> APIRouter:
        require_authenticated_user = AuthenticatedUserDependency(
            self.access_token_authenticator,
        )
        endpoint = CurrentUserEndpoint(require_authenticated_user)
        router = APIRouter(prefix="/identity", tags=["identity"])
        router.add_api_route(
            "/me",
            endpoint,
            methods=["GET"],
            response_model=dict[str, str],
            dependencies=[Depends(require_authenticated_user)],
        )
        return router

    def install(self, app: FastAPI) -> None:
        app.include_router(self.router())
