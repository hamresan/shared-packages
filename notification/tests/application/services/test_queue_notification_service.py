from notification.application.services.queue_notification_service import QueueNotificationService
from notification.domain.enums import NotificationChannel
from notification.public.commands import SendNotification
from tests.support.fakes import FakeNotificationQueue


async def test_queue_notification_service_maps_public_command_to_job_payload() -> None:
    queue = FakeNotificationQueue()
    service = QueueNotificationService(queue)

    reference = await service.send(
        SendNotification(
            channel=NotificationChannel.SMS,
            recipient="+96890000000",
            template_key="auth.otp",
            variables={"otp": "123456"},
        )
    )

    assert reference.job_id == "job-1"
    assert queue.payload is not None
    assert queue.payload.template_key == "auth.otp"
    assert queue.payload.variables == {"otp": "123456"}
