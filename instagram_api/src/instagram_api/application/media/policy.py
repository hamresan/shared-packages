"""Access policy for Instagram media reads."""

from instagram_api.domain import InstagramConnection

from .errors import (
    InstagramMediaConnectionUnavailableError,
    InstagramMediaPermissionRequiredError,
)

INSTAGRAM_MEDIA_READ_PERMISSION = "instagram_business_basic"


class InstagramMediaAccessPolicy:
    """Validates whether a selected connection can read owned media."""

    def validate_connection(self, connection: InstagramConnection) -> None:
        """Validate selected connection usability and media permission."""

        if not connection.is_usable:
            raise InstagramMediaConnectionUnavailableError(
                "Selected Instagram connection is not usable."
            )

        if INSTAGRAM_MEDIA_READ_PERMISSION not in connection.permissions:
            raise InstagramMediaPermissionRequiredError(
                f"Required permission is missing: {INSTAGRAM_MEDIA_READ_PERMISSION}"
            )
