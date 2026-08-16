from notification.application.contracts.queue import NotificationQueue
from notification.application.dto import NotificationJobPayload
from notification.public.commands import SendNotification
from notification.public.dto import NotificationReference
from notification.public.services import NotificationSender


class QueueNotificationService(NotificationSender):
    def __init__(self, queue: NotificationQueue) -> None:
        self._queue = queue

    async def send(self, command: SendNotification) -> NotificationReference:
        payload = NotificationJobPayload(
            channel=command.channel,
            recipient=command.recipient,
            template_key=command.template_key,
            locale=command.locale,
            variables=dict(command.variables),
        )
        return await self._queue.enqueue(payload)
