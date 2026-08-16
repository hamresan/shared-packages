from notification.application.dto import NotificationJobPayload
from notification.application.services.deliver_notification_service import DeliverNotificationService
from notification.domain.enums import NotificationChannel
from tests.support.fakes import FakeProvider, FakeProviderResolver, FakeTemplateRenderer


async def test_deliver_notification_service_renders_and_sends() -> None:
    provider = FakeProvider()
    service = DeliverNotificationService(
        renderer=FakeTemplateRenderer(),
        provider_resolver=FakeProviderResolver(provider),
    )

    result = await service.deliver(
        NotificationJobPayload(
            channel=NotificationChannel.SMS,
            recipient="+96890000000",
            template_key="auth.otp",
            locale="en",
            variables={"otp": "123456"},
        )
    )

    assert result.provider == "fake"
    assert provider.request is not None
    assert provider.request.recipient == "+96890000000"
    assert provider.request.message.body == "OTP 123456"
