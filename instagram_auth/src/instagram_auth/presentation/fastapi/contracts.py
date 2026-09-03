"""Host-supplied contracts used by the optional FastAPI adapter."""

from typing import Protocol

from fastapi import Request, Response

from instagram_auth.application.authorization.models import ValidatedInstagramAuthorization


class InstagramFastApiOwnerContext(Protocol):
    """Resolve host ownership without coupling auth to host session implementation."""

    async def optional_owner_user_id(self, request: Request) -> str | None: ...

    async def require_owner_user_id(self, request: Request) -> str: ...


class InstagramFastApiCallbackResponder(Protocol):
    """Let the host decide redirect/session behavior after callback validation."""

    async def respond(
        self,
        *,
        authorization_code: str,
        authorization: ValidatedInstagramAuthorization,
    ) -> Response: ...
