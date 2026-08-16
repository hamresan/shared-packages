from typing import TextIO

from notification.application.contracts.providers import NotificationProvider
from notification.application.dto import DeliveryRequest, DeliveryResult


class ConsoleNotificationProvider(NotificationProvider):
    def __init__(self, writer: TextIO) -> None:
        self._writer = writer

    async def send(self, request: DeliveryRequest) -> DeliveryResult:
        self._writer.write(
            f"[{request.channel.value}] {request.recipient}: {request.message.body}\n"
        )
        return DeliveryResult(provider="console")
