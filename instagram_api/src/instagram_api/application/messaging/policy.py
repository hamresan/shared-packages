"""Access policy for Instagram conversation and message reads."""

from instagram_api.domain import InstagramConnection

from .errors import (
    InstagramMessagingConnectionUnavailableError,
    InstagramMessagingPermissionRequiredError,
)

INSTAGRAM_BASIC_PERMISSION = "instagram_business_basic"
INSTAGRAM_MANAGE_MESSAGES_PERMISSION = "instagram_business_manage_messages"


class InstagramMessagingReadPolicy:
    """Validates whether a selected connection can read messaging data."""

    def validate_connection(self, connection: InstagramConnection) -> None:
        """Validate usability and required messaging permissions."""

        if not connection.is_usable:
            raise InstagramMessagingConnectionUnavailableError(
                "Selected Instagram connection is not usable."
            )

        required = {
            INSTAGRAM_BASIC_PERMISSION,
            INSTAGRAM_MANAGE_MESSAGES_PERMISSION,
        }
        missing = required.difference(connection.permissions)
        if missing:
            permission = sorted(missing)[0]
            raise InstagramMessagingPermissionRequiredError(
                f"Required permission is missing: {permission}"
            )
