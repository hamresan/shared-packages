from notification.public import (
    NotificationReference,
    NotificationSender,
    SendNotification,
)


class NullNotificationSender(NotificationSender):
    async def send(self, command: SendNotification) -> NotificationReference:
        return NotificationReference(job_id=f"unused-{command.template_key}")
