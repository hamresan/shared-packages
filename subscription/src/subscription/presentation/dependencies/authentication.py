from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class AuthenticatedActor:
    actor_id: str

    def __post_init__(self) -> None:
        if not self.actor_id.strip():
            raise ValueError("authenticated actor id must not be empty")


class AuthenticatedActorDependency(Protocol):
    async def __call__(self) -> AuthenticatedActor: ...
