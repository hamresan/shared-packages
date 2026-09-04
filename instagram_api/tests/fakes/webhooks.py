"""Webhook contract fakes."""

from instagram_api.application.contracts.webhooks import (
    InstagramWebhookParser,
    InstagramWebhookVerifier,
)
from instagram_api.domain import InstagramWebhookEvent


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
