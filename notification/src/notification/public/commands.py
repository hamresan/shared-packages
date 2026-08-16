from dataclasses import dataclass, field
from typing import TypeAlias

from notification.domain.enums import NotificationChannel

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


@dataclass(frozen=True, slots=True)
class SendNotification:
    channel: NotificationChannel
    recipient: str
    template_key: str
    locale: str = "en"
    variables: dict[str, JsonValue] = field(default_factory=dict)
