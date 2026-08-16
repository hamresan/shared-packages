from typing import Protocol

from notification.public.commands import SendNotification
from notification.public.dto import NotificationReference


class NotificationSender(Protocol):
    async def send(self, command: SendNotification) -> NotificationReference: ...
