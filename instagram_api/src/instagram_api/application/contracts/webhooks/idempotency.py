"""Idempotency boundary for Instagram webhook deliveries."""

from typing import Protocol


class InstagramWebhookIdempotencyStore(Protocol):
    """Coordinates durable atomic webhook-event processing."""

    async def acquire(self, event_id: str) -> bool:
        """Acquire processing ownership; return False for an existing event."""
        ...

    async def complete(self, event_id: str) -> None:
        """Mark a successfully dispatched event as completed."""
        ...

    async def release(self, event_id: str) -> None:
        """Release a failed processing claim so a later delivery can retry."""
        ...
