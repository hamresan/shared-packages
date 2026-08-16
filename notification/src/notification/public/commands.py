from dataclasses import dataclass, field

from notification.domain.enums import NotificationChannel

type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list[JsonValue] | dict[str, JsonValue]


@dataclass(frozen=True, slots=True)
class SendNotification:
    channel: NotificationChannel
    recipient: str
    template_key: str
    locale: str = "en"
    variables: dict[str, JsonValue] = field(default_factory=dict)
