from dataclasses import dataclass

from notification.application.contracts.providers import NotificationProviderResolver
from notification.application.contracts.queue import NotificationQueue
from notification.application.contracts.templates import MessageTemplateRenderer
from notification.application.services.deliver_notification_service import (
    DeliverNotificationService,
)
from notification.application.services.queue_notification_service import QueueNotificationService


@dataclass(frozen=True, slots=True)
class NotificationModuleConfig:
    queue: NotificationQueue
    renderer: MessageTemplateRenderer
    provider_resolver: NotificationProviderResolver


@dataclass(frozen=True, slots=True)
class NotificationModule:
    config: NotificationModuleConfig

    @property
    def sender(self) -> QueueNotificationService:
        return QueueNotificationService(self.config.queue)

    @property
    def delivery_service(self) -> DeliverNotificationService:
        return DeliverNotificationService(
            renderer=self.config.renderer,
            provider_resolver=self.config.provider_resolver,
        )
