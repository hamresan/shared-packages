"""Connection-health models for Instagram authorization lifecycle."""

from dataclasses import dataclass
from enum import StrEnum

from instagram_auth.baseline import InstagramPermission
from instagram_auth.domain import InstagramConnectionId


class InstagramConnectionHealthStatus(StrEnum):
    """Normalized usability state for one Instagram connection."""

    USABLE = "usable"
    REAUTHORIZATION_REQUIRED = "reauthorization_required"
    DISCONNECTED = "disconnected"


class InstagramConnectionHealthReason(StrEnum):
    """Reason a selected connection is not currently usable."""

    EXPIRED_CREDENTIAL = "expired_credential"
    REVOKED_CREDENTIAL = "revoked_credential"
    MISSING_PERMISSION = "missing_permission"
    CONNECTION_STATUS = "connection_status"


@dataclass(frozen=True, slots=True)
class InstagramConnectionHealth:
    """Explicit health result for one independently managed connection."""

    connection_id: InstagramConnectionId
    status: InstagramConnectionHealthStatus
    reasons: frozenset[InstagramConnectionHealthReason] = frozenset()
    missing_permissions: frozenset[InstagramPermission] = frozenset()
