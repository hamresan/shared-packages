"""Access policy for Instagram comment reads."""

from instagram_api.domain import InstagramConnection

from .errors import (
    InstagramCommentConnectionUnavailableError,
    InstagramCommentPermissionRequiredError,
)

INSTAGRAM_COMMENT_BASIC_PERMISSION = "instagram_business_basic"
INSTAGRAM_COMMENT_MANAGE_PERMISSION = "instagram_business_manage_comments"


class InstagramCommentAccessPolicy:
    """Validates whether a selected connection can read comments."""

    def validate_connection(self, connection: InstagramConnection) -> None:
        """Require a usable connection with comment-read permissions."""

        if not connection.is_usable:
            raise InstagramCommentConnectionUnavailableError(
                "Selected Instagram connection is not usable."
            )

        required_permissions = {
            INSTAGRAM_COMMENT_BASIC_PERMISSION,
            INSTAGRAM_COMMENT_MANAGE_PERMISSION,
        }
        missing_permissions = required_permissions.difference(connection.permissions)
        if missing_permissions:
            permission = sorted(missing_permissions)[0]
            raise InstagramCommentPermissionRequiredError(
                f"Required permission is missing: {permission}"
            )
