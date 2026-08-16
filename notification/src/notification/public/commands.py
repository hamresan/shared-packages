from dataclasses import dataclass, field

from notification.domain.enums import NotificationChannel
from notification.domain.types import JsonValue, empty_json_object


@dataclass(frozen=True, slots=True)
class SendNotification:
    channel: NotificationChannel
    recipient: str
    template_key: str
    locale: str = "en"
    variables: dict[str, JsonValue] = field(default_factory=empty_json_object)
