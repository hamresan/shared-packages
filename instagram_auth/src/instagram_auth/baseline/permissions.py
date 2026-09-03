"""Instagram permission registry and least-privilege request semantics."""

from collections.abc import Collection
from enum import StrEnum


class InstagramPermission(StrEnum):
    """Permissions recognized by the initial Instagram Login package contract."""

    BASIC = "instagram_business_basic"
    MANAGE_MESSAGES = "instagram_business_manage_messages"
    MANAGE_COMMENTS = "instagram_business_manage_comments"
    MANAGE_INSIGHTS = "instagram_business_manage_insights"
    CONTENT_PUBLISH = "instagram_business_content_publish"


CORE_PERMISSIONS = frozenset(
    {
        InstagramPermission.BASIC,
        InstagramPermission.MANAGE_MESSAGES,
        InstagramPermission.MANAGE_COMMENTS,
    }
)

OPTIONAL_PERMISSIONS = frozenset(
    {
        InstagramPermission.MANAGE_INSIGHTS,
        InstagramPermission.CONTENT_PUBLISH,
    }
)


def build_requested_permissions(
    optional_permissions: Collection[InstagramPermission] = (),
) -> frozenset[InstagramPermission]:
    """Build a least-privilege permission set from core plus approved optional scopes."""

    requested_optional = frozenset(optional_permissions)
    unsupported = requested_optional - OPTIONAL_PERMISSIONS
    if unsupported:
        unsupported_values = ", ".join(sorted(permission.value for permission in unsupported))
        raise ValueError(f"Unsupported optional Instagram permissions: {unsupported_values}")
    return CORE_PERMISSIONS | requested_optional
