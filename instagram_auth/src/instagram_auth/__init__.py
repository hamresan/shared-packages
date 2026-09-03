"""Instagram OAuth and authorization package."""

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

__all__ = [
    "CORE_PERMISSIONS",
    "OPTIONAL_PERMISSIONS",
    "InstagramAccountType",
    "InstagramConnectionState",
    "InstagramPermission",
    "InstagramProviderErrorKind",
    "build_requested_permissions",
    "is_eligible_account_type",
]
