"""Host-observable Instagram authorization security events."""

from dataclasses import dataclass
from enum import StrEnum

from instagram_auth.domain import InstagramConnectionId


class InstagramSecurityEventKind(StrEnum):
    """Security-significant Instagram authorization events."""

    CREDENTIAL_EXPIRED = "credential_expired"
    CREDENTIAL_REVOKED = "credential_revoked"
    PERMISSION_LOSS = "permission_loss"
    REPEATED_OAUTH_FAILURE = "repeated_oauth_failure"


@dataclass(frozen=True, slots=True)
class InstagramSecurityEvent:
    """Security event that contains no provider secret material."""

    connection_id: InstagramConnectionId
    kind: InstagramSecurityEventKind
