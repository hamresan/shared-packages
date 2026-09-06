"""Policies for outbound Instagram messaging."""

from instagram_api.domain import InstagramConnection, InstagramMessageSendRequest

from .errors import (
    InstagramMessagingConnectionUnavailableError,
    InstagramMessagingPermissionRequiredError,
)
from .send_errors import InstagramMessagePayloadInvalidError

INSTAGRAM_SEND_BASIC_PERMISSION = "instagram_business_basic"
INSTAGRAM_SEND_MESSAGE_PERMISSION = "instagram_business_manage_messages"
INSTAGRAM_TEXT_MESSAGE_MAX_LENGTH = 1000


class InstagramMessageSendAccessPolicy:
    """Validates connection eligibility for outbound messaging."""

    def validate_connection(self, connection: InstagramConnection) -> None:
        """Require a usable connection with outbound messaging permissions."""

        if not connection.is_usable:
            raise InstagramMessagingConnectionUnavailableError(
                "Selected Instagram connection is not usable."
            )

        required = {
            INSTAGRAM_SEND_BASIC_PERMISSION,
            INSTAGRAM_SEND_MESSAGE_PERMISSION,
        }
        missing = required.difference(connection.permissions)
        if missing:
            permission = sorted(missing)[0]
            raise InstagramMessagingPermissionRequiredError(
                f"Required permission is missing: {permission}"
            )


class InstagramMessagePayloadPolicy:
    """Validates supported outbound payload shapes."""

    def validate(self, request: InstagramMessageSendRequest) -> None:
        """Require exactly one supported message payload."""

        has_text = request.text is not None and bool(request.text.strip())
        has_attachment = request.attachment is not None

        if has_text == has_attachment:
            raise InstagramMessagePayloadInvalidError(
                "Exactly one of text or attachment must be provided."
            )

        if request.text is not None and not request.text.strip():
            raise InstagramMessagePayloadInvalidError("Message text must not be blank.")

        if (
            request.text is not None
            and len(request.text) > INSTAGRAM_TEXT_MESSAGE_MAX_LENGTH
        ):
            raise InstagramMessagePayloadInvalidError(
                f"Message text must not exceed {INSTAGRAM_TEXT_MESSAGE_MAX_LENGTH} characters."
            )

        if request.attachment is not None and not request.attachment.url.strip():
            raise InstagramMessagePayloadInvalidError("Attachment URL must not be blank.")
