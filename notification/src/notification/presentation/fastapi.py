from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from notification.domain.enums import NotificationChannel
from notification.public.commands import SendNotification
from notification.public.services import NotificationSender


class SendNotificationRequest(BaseModel):
    channel: NotificationChannel
    recipient: str = Field(min_length=1)
    template_key: str = Field(min_length=1)
    locale: str = Field(default="en", min_length=2)
    variables: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class SendNotificationResponse(BaseModel):
    job_id: str


def create_notification_router(sender: NotificationSender) -> APIRouter:
    router = APIRouter(prefix="/notifications", tags=["notifications"])

    @router.post(
        "/test", response_model=SendNotificationResponse, status_code=status.HTTP_202_ACCEPTED
    )
    async def send_test_notification(request: SendNotificationRequest) -> SendNotificationResponse:
        reference = await sender.send(
            SendNotification(
                channel=request.channel,
                recipient=request.recipient,
                template_key=request.template_key,
                locale=request.locale,
                variables=dict(request.variables),
            )
        )
        return SendNotificationResponse(job_id=reference.job_id)

    return router
