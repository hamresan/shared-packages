"""Keep production permission documentation aligned with implemented policies."""

from pathlib import Path

from instagram_api.application.accounts.policy import INSTAGRAM_BUSINESS_BASIC_PERMISSION
from instagram_api.application.comments.policy import INSTAGRAM_COMMENT_MANAGE_PERMISSION
from instagram_api.application.messaging.policy import INSTAGRAM_MANAGE_MESSAGES_PERMISSION

PRODUCTION_DOC = Path(__file__).parents[2] / "PRODUCTION.md"


def test_every_core_permission_is_justified_by_an_implemented_feature() -> None:
    documentation = PRODUCTION_DOC.read_text(encoding="utf-8")
    permissions = {
        INSTAGRAM_BUSINESS_BASIC_PERMISSION,
        INSTAGRAM_MANAGE_MESSAGES_PERMISSION,
        INSTAGRAM_COMMENT_MANAGE_PERMISSION,
    }

    for permission in permissions:
        assert f"`{permission}`" in documentation


def test_unimplemented_optional_permissions_are_not_declared_as_required() -> None:
    documentation = PRODUCTION_DOC.read_text(encoding="utf-8")

    assert "not required" in documentation
    assert "`instagram_business_manage_insights`" in documentation
    assert "`instagram_business_content_publish`" in documentation
