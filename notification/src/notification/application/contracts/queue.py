from typing import Protocol

from notification.application.dto import NotificationJobPayload
from notification.public.dto import NotificationReference


class NotificationQueue(Protocol):
    async def enqueue(self, payload: NotificationJobPayload) -> NotificationReference: ...
