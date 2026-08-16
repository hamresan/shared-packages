from notification.application.dto import DeliveryRequest, DeliveryResult, NotificationJobPayload
from notification.domain.enums import NotificationChannel
from notification.domain.value_objects import RenderedMessage
from notification.public.dto import NotificationReference


class FakeNotificationQueue:
    def __init__(self) -> None:
        self.payload: NotificationJobPayload | None = None

    async def enqueue(self, payload: NotificationJobPayload) -> NotificationReference:
        self.payload = payload
        return NotificationReference(job_id="job-1")


class FakeTemplateRenderer:
    def render(
        self,
        template_key: str,
        locale: str,
        channel: NotificationChannel,
        variables: dict[str, object],
    ) -> RenderedMessage:
        return RenderedMessage(subject=None, body=f"OTP {variables['otp']}")


class FakeProvider:
    def __init__(self) -> None:
        self.request: DeliveryRequest | None = None

    async def send(self, request: DeliveryRequest) -> DeliveryResult:
        self.request = request
        return DeliveryResult(provider="fake")


class FakeProviderResolver:
    def __init__(self, provider: FakeProvider) -> None:
        self._provider = provider

    def resolve(self, channel: NotificationChannel) -> FakeProvider:
        return self._provider
