from jinja2 import Environment

from notification.application.contracts.templates import (
    MessageTemplateRenderer,
    MessageTemplateRepository,
)
from notification.domain.enums import NotificationChannel
from notification.domain.types import JsonValue
from notification.domain.value_objects import RenderedMessage


class JinjaMessageTemplateRenderer(MessageTemplateRenderer):
    def __init__(self, repository: MessageTemplateRepository, environment: Environment) -> None:
        self._repository = repository
        self._environment = environment

    def render(
        self,
        template_key: str,
        locale: str,
        channel: NotificationChannel,
        variables: dict[str, JsonValue],
    ) -> RenderedMessage:
        source = self._repository.get(template_key, locale, channel)
        rendered = self._environment.from_string(source).render(**variables)
        if channel is NotificationChannel.EMAIL and "\n---subject---\n" in rendered:
            subject, body = rendered.split("\n---subject---\n", maxsplit=1)
            return RenderedMessage(subject=subject.strip(), body=body.strip())
        return RenderedMessage(subject=None, body=rendered.strip())
