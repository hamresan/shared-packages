"""Demonstration API-key authentication; do not use static demo identities in production."""

from collections.abc import Awaitable, Callable

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from scheduling.application.models import TrustedActor


def authenticated_demo_actor(api_key: str) -> Callable[[], Awaitable[TrustedActor]]:
    header = APIKeyHeader(name="X-API-Key", auto_error=False)

    async def require_actor(provided: str | None = Security(header)) -> TrustedActor:
        if provided != api_key:
            raise HTTPException(status_code=401, detail="Invalid API key.")
        return TrustedActor(tenant_id="demo-tenant", actor_id="demo-owner")

    return require_actor
