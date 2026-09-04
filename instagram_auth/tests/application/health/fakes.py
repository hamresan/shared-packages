"""Fakes for Instagram connection-health tests."""

from instagram_auth.application.contracts import InstagramSecurityEventSink
from instagram_auth.application.models import InstagramSecurityEvent


class FakeInstagramSecurityEventSink(InstagramSecurityEventSink):
    """Capture published security events for assertions."""

    def __init__(self) -> None:
        self.events: list[InstagramSecurityEvent] = []

    async def publish(self, event: InstagramSecurityEvent) -> None:
        self.events.append(event)
