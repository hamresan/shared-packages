"""Persistence boundary for short-lived OAuth authorization state."""

from typing import Protocol

from instagram_auth.application.authorization.models import InstagramAuthorizationState


class InstagramAuthorizationStateStore(Protocol):
    """Persist and atomically consume one-time OAuth authorization state."""

    async def save(self, authorization_state: InstagramAuthorizationState) -> None:
        """Persist a short-lived authorization state record."""
        ...

    async def consume(self, state: str) -> InstagramAuthorizationState | None:
        """Atomically remove and return a state record when it exists."""
        ...
