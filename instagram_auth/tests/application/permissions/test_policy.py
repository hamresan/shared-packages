from instagram_auth.application.permissions import (
    InstagramPermissionPolicy,
    InstagramPermissionStatus,
)
from instagram_auth.baseline import InstagramPermission


def test_permission_policy_reports_complete_grant() -> None:
    required = frozenset({InstagramPermission.BASIC, InstagramPermission.MANAGE_MESSAGES})

    result = InstagramPermissionPolicy().evaluate(
        required_permissions=required,
        granted_permissions=required | {InstagramPermission.MANAGE_COMMENTS},
    )

    assert result.status is InstagramPermissionStatus.COMPLETE
    assert result.missing_permissions == frozenset()
    assert result.requires_reauthorization is False


def test_permission_policy_reports_missing_required_permissions() -> None:
    result = InstagramPermissionPolicy().evaluate(
        required_permissions={InstagramPermission.BASIC, InstagramPermission.MANAGE_MESSAGES},
        granted_permissions={InstagramPermission.BASIC},
    )

    assert result.status is InstagramPermissionStatus.PARTIAL
    assert result.missing_permissions == frozenset({InstagramPermission.MANAGE_MESSAGES})
    assert result.requires_reauthorization is True
