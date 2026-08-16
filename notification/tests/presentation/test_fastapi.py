from fastapi import FastAPI
from fastapi.testclient import TestClient

from notification.application.services.queue_notification_service import QueueNotificationService
from notification.presentation.fastapi import create_notification_router
from tests.support.fakes import FakeNotificationQueue


def test_fastapi_adapter_queues_notification() -> None:
    queue = FakeNotificationQueue()
    app = FastAPI()
    app.include_router(create_notification_router(QueueNotificationService(queue)))
    client = TestClient(app)

    response = client.post(
        "/notifications/test",
        json={
            "channel": "sms",
            "recipient": "+96890000000",
            "template_key": "auth.otp",
            "variables": {"otp": "123456"},
        },
    )

    assert response.status_code == 202
    assert response.json() == {"job_id": "job-1"}
    assert queue.payload is not None
    assert queue.payload.template_key == "auth.otp"
