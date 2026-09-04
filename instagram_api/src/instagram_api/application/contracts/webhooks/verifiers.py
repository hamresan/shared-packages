"""Instagram webhook authenticity contracts."""

from typing import Protocol


class InstagramWebhookVerifier(Protocol):
    """Verifies webhook authenticity without parsing provider payloads."""

    def verify(self, payload: bytes, signature: str | None) -> bool:
        """Return whether the webhook payload is authentic."""
        ...
