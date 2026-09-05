"""Host identity handoff and connection-linking models."""

from dataclasses import dataclass
from enum import StrEnum

from instagram_auth.application.models import InstagramAuthorizationGrant
from instagram_auth.domain import InstagramConnectionId, InstagramExternalIdentity


class InstagramHostLinkAction(StrEnum):
    """Host action required after Instagram identity resolution."""

    RESOLVE_LOCAL_USER = "resolve_local_user"
    ATTACH_TO_EXISTING_OWNER = "attach_to_existing_owner"


@dataclass(frozen=True, slots=True)
class InstagramHostIdentityHandoff:
    """Secret-free identity result handed to host composition."""

    identity: InstagramExternalIdentity
    action: InstagramHostLinkAction
    owner_user_id: str | None = None


@dataclass(frozen=True, slots=True)
class LinkInstagramAuthorizationCommand:
    """Explicit host decision for persisting one Instagram authorization."""

    owner_user_id: str
    identity: InstagramExternalIdentity
    grant: InstagramAuthorizationGrant


@dataclass(frozen=True, slots=True)
class ReauthorizeInstagramConnectionCommand:
    """Explicit command for refreshing one selected Instagram connection."""

    owner_user_id: str
    connection_id: InstagramConnectionId
    identity: InstagramExternalIdentity
    grant: InstagramAuthorizationGrant


@dataclass(frozen=True, slots=True)
class InstagramConnectionLinkResult:
    """Result of linking an Instagram authorization to one host owner."""

    connection_id: InstagramConnectionId
    owner_user_id: str
    created: bool
