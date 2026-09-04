"""Outbound Instagram messaging policy tests."""

import pytest

from instagram_api.application.messaging import (
    InstagramMessagePayloadInvalidError,
    InstagramMessagePayloadPolicy,
    InstagramMessageSendAccessPolicy,
    InstagramMessagingConnectionUnavailableError,
    InstagramMessagingPermissionRequiredError,
)
from instagram_api.domain import (
    InstagramAccountId,
    InstagramConnection,
    InstagramConnectionId,
    InstagramMessageAttachment,
    InstagramMessageAttachmentType,
    InstagramMessageSendRequest,
    InstagramUserId,
)


def build_connection(
    *,
    usable: bool = True,
    permissions: frozenset[str] = frozenset(
        {
            "instagram_business_basic",
            "instagram_business_manage_messages",
        }
    ),
) -> InstagramConnection:
    return InstagramConnection(
        id=InstagramConnectionId("connection"),
        provider_account_id=InstagramAccountId("account"),
        permissions=permissions,
        is_usable=usable,
    )


def test_send_access_policy_accepts_required_permissions() -> None:
    InstagramMessageSendAccessPolicy().validate_connection(build_connection())


@pytest.mark.parametrize(
    ("connection", "error_type"),
    [
        (
            build_connection(usable=False),
            InstagramMessagingConnectionUnavailableError,
        ),
        (
            build_connection(permissions=frozenset({"instagram_business_manage_messages"})),
            InstagramMessagingPermissionRequiredError,
        ),
        (
            build_connection(permissions=frozenset({"instagram_business_basic"})),
            InstagramMessagingPermissionRequiredError,
        ),
    ],
)
def test_send_access_policy_rejects_ineligible_connection(
    connection: InstagramConnection,
    error_type: type[Exception],
) -> None:
    with pytest.raises(error_type):
        InstagramMessageSendAccessPolicy().validate_connection(connection)


@pytest.mark.parametrize(
    "request",
    [
        InstagramMessageSendRequest(InstagramUserId("recipient")),
        InstagramMessageSendRequest(InstagramUserId("recipient"), text="   "),
        InstagramMessageSendRequest(
            InstagramUserId("recipient"),
            text="hello",
            attachment=InstagramMessageAttachment(
                InstagramMessageAttachmentType.IMAGE,
                "https://example.com/image.jpg",
            ),
        ),
        InstagramMessageSendRequest(
            InstagramUserId("recipient"),
            attachment=InstagramMessageAttachment(
                InstagramMessageAttachmentType.IMAGE,
                "   ",
            ),
        ),
    ],
)
def test_payload_policy_rejects_invalid_payloads(
    request: InstagramMessageSendRequest,
) -> None:
    with pytest.raises(InstagramMessagePayloadInvalidError):
        InstagramMessagePayloadPolicy().validate(request)


def test_payload_policy_accepts_text_and_media_payloads() -> None:
    policy = InstagramMessagePayloadPolicy()

    policy.validate(
        InstagramMessageSendRequest(
            InstagramUserId("recipient"),
            text="hello",
        )
    )
    policy.validate(
        InstagramMessageSendRequest(
            InstagramUserId("recipient"),
            attachment=InstagramMessageAttachment(
                InstagramMessageAttachmentType.VIDEO,
                "https://example.com/video.mp4",
            ),
        )
    )
