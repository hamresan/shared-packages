from typing import Protocol

from notification.domain.enums import NotificationChannel
from notification.domain.types import JsonValue
from notification.domain.value_objects import RenderedMessage


class MessageTemplateRepository(Protocol):
    def get(self, template_key: str, locale: str, channel: NotificationChannel) -> str: ...


class MessageTemplateRenderer(Protocol):
    def render(
        self,
        template_key: str,
        locale: str,
        channel: NotificationChannel,
        variables: dict[str, JsonValue],
    ) -> RenderedMessage: ...
