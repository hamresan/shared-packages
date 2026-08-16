from notification.application.contracts.providers import NotificationProvider, NotificationProviderResolver
from notification.domain.enums import NotificationChannel


class StaticNotificationProviderResolver(NotificationProviderResolver):
    def __init__(self, providers: dict[NotificationChannel, NotificationProvider]) -> None:
        self._providers = dict(providers)

    def resolve(self, channel: NotificationChannel) -> NotificationProvider:
        try:
            return self._providers[channel]
        except KeyError as exc:
            raise ValueError(f"No notification provider configured for channel: {channel}") from exc
