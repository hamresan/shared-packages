"""Protected Instagram credential persistence model."""

from dataclasses import dataclass
from datetime import datetime

from instagram_auth.domain import InstagramConnectionId


@dataclass(frozen=True, slots=True)
class InstagramProtectedCredential:
    """Protected credential and lifecycle metadata for one explicit connection."""

    connection_id: InstagramConnectionId
    protected_access_token: str
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
    last_validated_at: datetime | None = None
