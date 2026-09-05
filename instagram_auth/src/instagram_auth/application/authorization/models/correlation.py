"""Host correlation metadata preserved across OAuth authorization."""

from dataclasses import dataclass
from enum import StrEnum


class InstagramAuthorizationFlow(StrEnum):
    """Host intent for an Instagram authorization attempt."""

    LOGIN = "login"
    CONNECT_ACCOUNT = "connect_account"
    RECONNECT_ACCOUNT = "reconnect_account"


@dataclass(frozen=True, slots=True)
class InstagramAuthorizationCorrelation:
    """Non-secret host context bound to one authorization attempt."""

    flow: InstagramAuthorizationFlow
    owner_user_id: str | None = None
    connection_id: str | None = None
