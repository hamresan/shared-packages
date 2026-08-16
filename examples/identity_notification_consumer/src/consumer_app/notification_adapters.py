from notification.application.contracts.providers import NotificationProviderResolver
from notification.application.contracts.queue import NotificationQueue
from notification.application.contracts.templates import MessageTemplateRenderer
from notification.application.dto import NotificationJobPayload
from notification.domain.enums import NotificationChannel
from notification.domain.value_objects import RenderedMessage
from notification.public import NotificationReference


class InMemoryNotificationQueue(NotificationQueue):
    def __init__(self) -> None:
        self.items: list[NotificationJobPayload] = []

    async def enqueue(self, payload: NotificationJobPayload) -> NotificationReference:
        self.items.append(payload)
        return NotificationReference(job_id=str(len(self.items)))


class UnusedTemplateRenderer(MessageTemplateRenderer):
    async def render(
        self,
        template_key: str,
        locale: str,
        variables: dict[str, object],
    ) -> RenderedMessage:
        raise AssertionError("Delivery rendering is outside this smoke test")


class UnusedProviderResolver(NotificationProviderResolver):
    def resolve(self, channel: NotificationChannel):
        raise AssertionError("Delivery provider resolution is outside this smoke test")
