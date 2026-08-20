from notification.public import NotificationChannel, NotificationSender, SendNotification

from identity.application.contracts.otp_delivery import OtpDelivery
from identity.domain import IdentityType, OtpPurpose


class NotificationOtpDelivery(OtpDelivery):
    def __init__(self, notification_sender: NotificationSender) -> None:
        self._notification_sender = notification_sender

    async def send(
        self,
        *,
        identity_type: IdentityType,
        destination: str,
        code: str,
        purpose: OtpPurpose,
        locale: str | None,
    ) -> None:
        channel = (
            NotificationChannel.SMS
            if identity_type is IdentityType.MOBILE
            else NotificationChannel.EMAIL
        )
        await self._notification_sender.send(
            SendNotification(
                channel=channel,
                recipient=destination,
                template_key="identity.otp",
                locale=locale,
                variables={"otp": code, "purpose": purpose.value},
            )
        )
