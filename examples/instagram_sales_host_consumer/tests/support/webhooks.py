"""Webhook transport-boundary fakes for the host integration test."""

from instagram_api.application.contracts import (
    InstagramWebhookIdempotencyStore,
    InstagramWebhookParser,
    InstagramWebhookVerifier,
)
from instagram_api.domain import InstagramWebhookEvent


class AcceptingWebhookVerifier(InstagramWebhookVerifier):
    """Accepts test webhook deliveries."""

    def verify(self, payload: bytes, signature: str | None) -> bool:
        del payload, signature
        return True


class StaticWebhookParser(InstagramWebhookParser):
    """Returns one configured normalized event."""

    def __init__(self, event: InstagramWebhookEvent) -> None:
        self._event = event

    def parse(self, payload: bytes) -> tuple[InstagramWebhookEvent, ...]:
        del payload
        return (self._event,)


class InMemoryWebhookIdempotencyStore(InstagramWebhookIdempotencyStore):
    """Small host test implementation of the API idempotency contract."""

    def __init__(self) -> None:
        self._events: set[str] = set()

    async def acquire(self, event_id: str) -> bool:
        if event_id in self._events:
            return False
        self._events.add(event_id)
        return True

    async def complete(self, event_id: str) -> None:
        self._events.add(event_id)

    async def release(self, event_id: str) -> None:
        self._events.discard(event_id)
