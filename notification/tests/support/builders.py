from notification.application.dto import DeliveryRequest
from notification.domain.enums import NotificationChannel
from notification.domain.value_objects import RenderedMessage


def build_delivery_request(
    *,
    channel: NotificationChannel = NotificationChannel.SMS,
    recipient: str = "+96890000000",
    subject: str | None = None,
    body: str = "Your OTP is 123456",
    template_key: str = "auth.otp",
) -> DeliveryRequest:
    return DeliveryRequest(
        channel=channel,
        recipient=recipient,
        message=RenderedMessage(subject=subject, body=body),
        template_key=template_key,
    )
