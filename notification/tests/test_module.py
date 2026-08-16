from notification.application.services.deliver_notification_service import DeliverNotificationService
from notification.application.services.queue_notification_service import QueueNotificationService
from notification.module import NotificationModule, NotificationModuleConfig
from tests.support.fakes import (
    FakeNotificationQueue,
    FakeProvider,
    FakeProviderResolver,
    FakeTemplateRenderer,
)


def test_notification_module_wires_services() -> None:
    queue = FakeNotificationQueue()
    provider = FakeProvider()
    module = NotificationModule(
        NotificationModuleConfig(
            queue=queue,
            renderer=FakeTemplateRenderer(),
            provider_resolver=FakeProviderResolver(provider),
        )
    )

    assert isinstance(module.sender, QueueNotificationService)
    assert isinstance(module.delivery_service, DeliverNotificationService)
