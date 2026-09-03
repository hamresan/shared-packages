"""In-memory fake for one-time authorization state persistence."""

from instagram_auth.application.authorization.models import InstagramAuthorizationState
from instagram_auth.application.contracts import InstagramAuthorizationStateStore


class FakeInstagramAuthorizationStateStore(InstagramAuthorizationStateStore):
    """Store authorization state in memory and consume it atomically for tests."""

    def __init__(self) -> None:
        self._states: dict[str, InstagramAuthorizationState] = {}

    async def save(self, authorization_state: InstagramAuthorizationState) -> None:
        self._states[authorization_state.state] = authorization_state

    async def consume(self, state: str) -> InstagramAuthorizationState | None:
        return self._states.pop(state, None)
