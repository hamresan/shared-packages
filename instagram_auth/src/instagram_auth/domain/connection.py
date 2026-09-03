"""Instagram connection domain entity."""

from dataclasses import dataclass
from datetime import datetime

from instagram_auth.baseline import InstagramAccountType, InstagramPermission
from instagram_auth.domain.connection_id import InstagramConnectionId
from instagram_auth.domain.status import InstagramConnectionStatus


@dataclass(frozen=True, slots=True)
class InstagramConnection:
    """Independent authorization resource owned by one host user."""

    id: InstagramConnectionId
    owner_user_id: str
    instagram_account_id: str
    username: str
    account_type: InstagramAccountType
    permissions: frozenset[InstagramPermission]
    status: InstagramConnectionStatus
    connected_at: datetime
    credential_expires_at: datetime | None = None
    revoked_at: datetime | None = None
    last_validated_at: datetime | None = None
    version: int = 1
