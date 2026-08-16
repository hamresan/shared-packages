from notification.application.contracts.providers import NotificationProviderResolver
from notification.application.contracts.templates import MessageTemplateRenderer
from notification.application.dto import DeliveryRequest, DeliveryResult, NotificationJobPayload


class DeliverNotificationService:
    def __init__(
        self,
        renderer: MessageTemplateRenderer,
        provider_resolver: NotificationProviderResolver,
    ) -> None:
        self._renderer = renderer
        self._provider_resolver = provider_resolver

    async def deliver(self, payload: NotificationJobPayload) -> DeliveryResult:
        message = self._renderer.render(
            payload.template_key,
            payload.locale,
            payload.channel,
            payload.variables,
        )
        provider = self._provider_resolver.resolve(payload.channel)
        return await provider.send(
            DeliveryRequest(
                channel=payload.channel,
                recipient=payload.recipient,
                message=message,
                template_key=payload.template_key,
            )
        )
