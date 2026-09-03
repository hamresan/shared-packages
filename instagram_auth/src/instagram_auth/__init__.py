"""Instagram OAuth and authorization package."""

from instagram_auth.application import (
    Clock,
    InstagramAccessTokenProtector,
    InstagramAuthorizationGrant,
    InstagramAuthorizationProvider,
    InstagramConnectionLister,
    InstagramConnectionReader,
    InstagramConnectionRepository,
    StateGenerator,
)
from instagram_auth.baseline import (
    CORE_PERMISSIONS,
    OPTIONAL_PERMISSIONS,
    InstagramAccountType,
    InstagramConnectionState,
    InstagramPermission,
    InstagramProviderErrorKind,
    build_requested_permissions,
    is_eligible_account_type,
)
from instagram_auth.domain import (
    InstagramConnection,
    InstagramConnectionId,
    InstagramConnectionStatus,
    InstagramExternalIdentity,
)

__all__ = [
    "CORE_PERMISSIONS",
    "OPTIONAL_PERMISSIONS",
    "Clock",
    "InstagramAccessTokenProtector",
    "InstagramAccountType",
    "InstagramAuthorizationGrant",
    "InstagramAuthorizationProvider",
    "InstagramConnection",
    "InstagramConnectionId",
    "InstagramConnectionLister",
    "InstagramConnectionReader",
    "InstagramConnectionRepository",
    "InstagramConnectionState",
    "InstagramConnectionStatus",
    "InstagramExternalIdentity",
    "InstagramPermission",
    "InstagramProviderErrorKind",
    "StateGenerator",
    "build_requested_permissions",
    "is_eligible_account_type",
]
