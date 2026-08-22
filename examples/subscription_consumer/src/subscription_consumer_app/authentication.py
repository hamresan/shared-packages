from subscription.presentation import AuthenticatedActor, AuthenticatedActorDependency


class StaticAuthenticatedActorDependency(AuthenticatedActorDependency):
    def __init__(self, actor_id: str) -> None:
        self._actor = AuthenticatedActor(actor_id=actor_id)

    async def __call__(self) -> AuthenticatedActor:
        return self._actor
