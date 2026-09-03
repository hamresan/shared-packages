"""Fakes for optional FastAPI host boundaries."""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from instagram_auth.application.authorization.models import ValidatedInstagramAuthorization
from instagram_auth.presentation.fastapi.contracts import (
    InstagramFastApiCallbackResponder,
    InstagramFastApiOwnerContext,
)


class FakeInstagramFastApiOwnerContext(InstagramFastApiOwnerContext):
    """Deterministic host ownership context for route tests."""

    def __init__(self, owner_user_id: str | None) -> None:
        self.owner_user_id = owner_user_id

    async def optional_owner_user_id(self, request: Request) -> str | None:
        del request
        return self.owner_user_id

    async def require_owner_user_id(self, request: Request) -> str:
        del request
        if self.owner_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )
        return self.owner_user_id


class FakeInstagramFastApiCallbackResponder(InstagramFastApiCallbackResponder):
    """Capture validated callback data while simulating host-owned behavior."""

    def __init__(self) -> None:
        self.authorization_code: str | None = None
        self.authorization: ValidatedInstagramAuthorization | None = None

    async def respond(
        self,
        *,
        authorization_code: str,
        authorization: ValidatedInstagramAuthorization,
    ) -> JSONResponse:
        self.authorization_code = authorization_code
        self.authorization = authorization
        return JSONResponse({"handled": True})
