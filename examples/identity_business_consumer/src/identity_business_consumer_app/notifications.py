from notification.application.contracts.providers import (
    NotificationProvider,
    NotificationProviderResolver,
)
from notification.application.contracts.queue import NotificationQueue
from notification.application.contracts.templates import MessageTemplateRenderer
from notification.application.dto import NotificationJobPayload
from notification.domain.enums import NotificationChannel
from notification.domain.types import JsonValue
from notification.domain.value_objects import RenderedMessage
from notification.public import NotificationReference


class CapturingNotificationQueue(NotificationQueue):
    def __init__(self) -> None:
        self.messages: list[NotificationJobPayload] = []

    async def enqueue(self, payload: NotificationJobPayload) -> NotificationReference:
        self.messages.append(payload)
        return NotificationReference(job_id=str(len(self.messages)))


class UnusedTemplateRenderer(MessageTemplateRenderer):
    def render(
        self,
        template_key: str,
        locale: str,
        channel: NotificationChannel,
        variables: dict[str, JsonValue],
    ) -> RenderedMessage:
        raise RuntimeError("Delivery workers are not part of this sample")


class UnusedProviderResolver(NotificationProviderResolver):
    def resolve(self, channel: NotificationChannel) -> NotificationProvider:
        raise RuntimeError("Delivery workers are not part of this sample")
