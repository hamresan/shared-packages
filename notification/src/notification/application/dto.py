from dataclasses import dataclass

from notification.domain.enums import NotificationChannel
from notification.domain.types import JsonValue
from notification.domain.value_objects import RenderedMessage


@dataclass(frozen=True, slots=True)
class DeliveryRequest:
    channel: NotificationChannel
    recipient: str
    message: RenderedMessage
    template_key: str


@dataclass(frozen=True, slots=True)
class DeliveryResult:
    provider: str
    provider_message_id: str | None = None


@dataclass(frozen=True, slots=True)
class NotificationJobPayload:
    channel: NotificationChannel
    recipient: str
    template_key: str
    locale: str
    variables: dict[str, JsonValue]
