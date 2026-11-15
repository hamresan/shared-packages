"""Test authentication source isolated from application input."""

from fastapi import HTTPException

from scheduling.application.models import TrustedActor


class FakeActorProvider:
    def __init__(self, actor: TrustedActor) -> None:
        self.actor = actor
        self.authenticated = True

    async def __call__(self) -> TrustedActor:
        if not self.authenticated:
            raise HTTPException(status_code=401, detail="Unauthenticated.")
        return self.actor
