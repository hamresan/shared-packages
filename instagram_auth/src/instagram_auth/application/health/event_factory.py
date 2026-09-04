"""Security-event factory for connection-health changes."""

from instagram_auth.application.models.security_event import (
    InstagramSecurityEvent,
    InstagramSecurityEventKind,
)

from .models import InstagramConnectionHealth, InstagramConnectionHealthReason


class InstagramHealthSecurityEventFactory:
    """Map health reasons to host-observable security events."""

    def build(self, health: InstagramConnectionHealth) -> tuple[InstagramSecurityEvent, ...]:
        mapping = {
            InstagramConnectionHealthReason.EXPIRED_CREDENTIAL: (
                InstagramSecurityEventKind.CREDENTIAL_EXPIRED
            ),
            InstagramConnectionHealthReason.REVOKED_CREDENTIAL: (
                InstagramSecurityEventKind.CREDENTIAL_REVOKED
            ),
            InstagramConnectionHealthReason.MISSING_PERMISSION: (
                InstagramSecurityEventKind.PERMISSION_LOSS
            ),
        }
        return tuple(
            InstagramSecurityEvent(connection_id=health.connection_id, kind=kind)
            for reason, kind in mapping.items()
            if reason in health.reasons
        )
