"""Stage 0 provider capability baseline."""

from instagram_auth.baseline.account_types import InstagramAccountType, is_eligible_account_type
from instagram_auth.baseline.permissions import (
    CORE_PERMISSIONS,
    OPTIONAL_PERMISSIONS,
    InstagramPermission,
    build_requested_permissions,
)
from instagram_auth.baseline.vocabulary import InstagramConnectionState, InstagramProviderErrorKind

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
