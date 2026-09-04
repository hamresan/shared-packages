"""Instagram webhook parsing contracts."""

from typing import Protocol

from instagram_api.domain.webhooks import InstagramWebhookEvent


class InstagramWebhookParser(Protocol):
    """Parses provider payloads into package-owned event envelopes."""

    def parse(self, payload: bytes) -> tuple[InstagramWebhookEvent, ...]:
        """Return normalized events found in the webhook payload."""
        ...
