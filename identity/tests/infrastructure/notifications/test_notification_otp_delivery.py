import pytest
from notification.public import NotificationChannel

from identity.domain import IdentityType, OtpPurpose
from identity.infrastructure.notifications import NotificationOtpDelivery
from tests.support.integrations import FakeNotificationSender


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("identity_type", "expected_channel"),
    [
        (IdentityType.MOBILE, NotificationChannel.SMS),
        (IdentityType.EMAIL, NotificationChannel.EMAIL),
    ],
)
async def test_send_maps_identity_type_to_notification_channel(
    identity_type: IdentityType,
    expected_channel: NotificationChannel,
) -> None:
    sender = FakeNotificationSender()
    delivery = NotificationOtpDelivery(sender)

    await delivery.send(
        identity_type=identity_type,
        destination="recipient",
        code="123456",
        purpose=OtpPurpose.LOGIN,
        locale="en",
    )

    command = sender.commands[-1]

    assert command.channel is expected_channel
    assert command.recipient == "recipient"
    assert command.template_key == "identity.otp"
    assert command.locale == "en"
    assert command.variables == {"otp": "123456", "purpose": "login"}
