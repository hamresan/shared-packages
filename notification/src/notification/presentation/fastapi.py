from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from notification.domain.enums import NotificationChannel
from notification.domain.types import JsonValue, empty_json_object
from notification.public.commands import SendNotification
from notification.public.services import NotificationSender


class SendNotificationRequest(BaseModel):
    channel: NotificationChannel
    recipient: str = Field(min_length=1)
    template_key: str = Field(min_length=1)
    locale: str = Field(default="en", min_length=2)
    variables: dict[str, JsonValue] = Field(default_factory=empty_json_object)


class SendNotificationResponse(BaseModel):
    job_id: str


class SendTestNotificationEndpoint:
    def __init__(self, sender: NotificationSender) -> None:
        self._sender = sender

    async def __call__(self, request: SendNotificationRequest) -> SendNotificationResponse:
        reference = await self._sender.send(
            SendNotification(
                channel=request.channel,
                recipient=request.recipient,
                template_key=request.template_key,
                locale=request.locale,
                variables=dict(request.variables),
            )
        )
        return SendNotificationResponse(job_id=reference.job_id)


def create_notification_router(sender: NotificationSender) -> APIRouter:
    router = APIRouter(prefix="/notifications", tags=["notifications"])
    router.add_api_route(
        "/test",
        SendTestNotificationEndpoint(sender),
        methods=["POST"],
        response_model=SendNotificationResponse,
        status_code=status.HTTP_202_ACCEPTED,
    )
    return router
