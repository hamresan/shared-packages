import pytest

from instagram_auth.baseline import (
    CORE_PERMISSIONS,
    OPTIONAL_PERMISSIONS,
    InstagramPermission,
    build_requested_permissions,
)


def test_core_permissions_match_stage_zero_contract() -> None:
    assert CORE_PERMISSIONS == {
        InstagramPermission.BASIC,
        InstagramPermission.MANAGE_MESSAGES,
        InstagramPermission.MANAGE_COMMENTS,
    }


def test_optional_registry_does_not_expand_default_request() -> None:
    assert OPTIONAL_PERMISSIONS == {
        InstagramPermission.MANAGE_INSIGHTS,
        InstagramPermission.CONTENT_PUBLISH,
    }
    assert build_requested_permissions() == CORE_PERMISSIONS


def test_requested_permissions_include_only_selected_optional_permissions() -> None:
    requested = build_requested_permissions({InstagramPermission.MANAGE_INSIGHTS})

    assert requested == CORE_PERMISSIONS | {InstagramPermission.MANAGE_INSIGHTS}
    assert InstagramPermission.CONTENT_PUBLISH not in requested


def test_core_permission_cannot_be_passed_as_optional_permission() -> None:
    with pytest.raises(ValueError, match="instagram_business_basic"):
        build_requested_permissions({InstagramPermission.BASIC})
