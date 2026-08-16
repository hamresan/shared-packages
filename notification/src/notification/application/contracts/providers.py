from typing import Protocol

from notification.application.dto import DeliveryRequest, DeliveryResult
from notification.domain.enums import NotificationChannel


class NotificationProvider(Protocol):
    async def send(self, request: DeliveryRequest) -> DeliveryResult: ...


class NotificationProviderResolver(Protocol):
    def resolve(self, channel: NotificationChannel) -> NotificationProvider: ...
