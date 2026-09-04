"""Webhook contract fakes."""

from instagram_api.application.contracts.webhooks import (
    InstagramWebhookConnectionResolver,
    InstagramWebhookEventDispatcher,
    InstagramWebhookIdempotencyStore,
    InstagramWebhookParser,
    InstagramWebhookVerifier,
)
from instagram_api.domain import (
    InstagramAccountId,
    InstagramConnectionId,
    InstagramWebhookEvent,
)


class FakeInstagramWebhookVerifier(InstagramWebhookVerifier):
    """Fake verifier with configurable result."""

    def __init__(self, result: bool) -> None:
        self._result = result

    def verify(self, payload: bytes, signature: str | None) -> bool:
        del payload, signature
        return self._result


class FakeInstagramWebhookParser(InstagramWebhookParser):
    """Fake parser with preconfigured normalized events."""

    def __init__(self, events: tuple[InstagramWebhookEvent, ...]) -> None:
        self._events = events

    def parse(self, payload: bytes) -> tuple[InstagramWebhookEvent, ...]:
        del payload
        return self._events


class FakeInstagramWebhookIdempotencyStore(InstagramWebhookIdempotencyStore):
    """In-memory atomic claim fake for webhook processor tests."""

    def __init__(self) -> None:
        self.in_progress: set[str] = set()
        self.completed: set[str] = set()
        self.acquire_calls: list[str] = []
        self.complete_calls: list[str] = []
        self.release_calls: list[str] = []

    async def acquire(self, event_id: str) -> bool:
        self.acquire_calls.append(event_id)
        if event_id in self.in_progress or event_id in self.completed:
            return False
        self.in_progress.add(event_id)
        return True

    async def complete(self, event_id: str) -> None:
        self.complete_calls.append(event_id)
        self.in_progress.remove(event_id)
        self.completed.add(event_id)

    async def release(self, event_id: str) -> None:
        self.release_calls.append(event_id)
        self.in_progress.discard(event_id)


class FakeInstagramWebhookConnectionResolver(InstagramWebhookConnectionResolver):
    """Fake host resolver keyed by provider Instagram account ID."""

    def __init__(
        self,
        connections: dict[InstagramAccountId, InstagramConnectionId],
    ) -> None:
        self._connections = connections
        self.calls: list[InstagramAccountId] = []

    async def resolve(
        self,
        provider_account_id: InstagramAccountId,
    ) -> InstagramConnectionId:
        self.calls.append(provider_account_id)
        return self._connections[provider_account_id]


class FakeInstagramWebhookEventDispatcher(InstagramWebhookEventDispatcher):
    """Fake host dispatcher with optional failure."""

    def __init__(self, fail_event_id: str | None = None) -> None:
        self._fail_event_id = fail_event_id
        self.events: list[tuple[InstagramConnectionId, InstagramWebhookEvent]] = []

    async def dispatch(
        self,
        connection_id: InstagramConnectionId,
        event: InstagramWebhookEvent,
    ) -> None:
        if event.event_id == self._fail_event_id:
            raise RuntimeError("dispatch failed")
        self.events.append((connection_id, event))
