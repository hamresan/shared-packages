from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AuthenticatedActor:
    user_id: UUID


AuthenticatedActorDependency = Callable[..., Awaitable[AuthenticatedActor]]
