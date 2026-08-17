from uuid import UUID, uuid4

from fastapi import HTTPException, status

from store.presentation import AuthenticatedActor


class FakeAuthenticatedActorDependency:
    def __init__(self, actor: AuthenticatedActor | None) -> None:
        self.actor = actor

    async def __call__(self) -> AuthenticatedActor:
        if self.actor is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
        return self.actor


class ActorBuilder:
    def __init__(self, user_id: UUID | None = None) -> None:
        self.user_id = user_id or uuid4()

    def build(self) -> AuthenticatedActor:
        return AuthenticatedActor(user_id=self.user_id)
