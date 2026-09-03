"""Required-permission evaluation policy."""

from collections.abc import Collection

from instagram_auth.baseline import InstagramPermission

from .models import InstagramPermissionEvaluation, InstagramPermissionStatus


class InstagramPermissionPolicy:
    """Compare granted permissions with the host-required permission set."""

    def evaluate(
        self,
        *,
        required_permissions: Collection[InstagramPermission],
        granted_permissions: Collection[InstagramPermission],
    ) -> InstagramPermissionEvaluation:
        required = frozenset(required_permissions)
        granted = frozenset(granted_permissions)
        missing = required - granted
        status = (
            InstagramPermissionStatus.COMPLETE
            if not missing
            else InstagramPermissionStatus.PARTIAL
        )
        return InstagramPermissionEvaluation(
            status=status,
            granted_permissions=granted,
            missing_permissions=missing,
        )
