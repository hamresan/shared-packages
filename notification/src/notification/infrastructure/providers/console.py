from notification.application.contracts.providers import NotificationProvider
from notification.application.dto import DeliveryRequest, DeliveryResult


class ConsoleNotificationProvider(NotificationProvider):
    def __init__(self, writer: object) -> None:
        self._writer = writer

    async def send(self, request: DeliveryRequest) -> DeliveryResult:
        write = self._writer.write
        write(f"[{request.channel.value}] {request.recipient}: {request.message.body}\n")
        return DeliveryResult(provider="console")
