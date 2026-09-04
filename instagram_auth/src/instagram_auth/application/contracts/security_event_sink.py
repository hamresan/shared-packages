"""Security-event publishing contract."""

from typing import Protocol

from instagram_auth.application.models.security_event import InstagramSecurityEvent


class InstagramSecurityEventSink(Protocol):
    """Publish host-observable Instagram authorization security events."""

    async def publish(self, event: InstagramSecurityEvent) -> None:
        """Publish one security event without exposing provider secrets."""
        ...
