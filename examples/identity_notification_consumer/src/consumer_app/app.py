from dataclasses import dataclass

from fastapi import FastAPI
from identity import IdentityModule, IdentityModuleConfig
from notification import NotificationModule, NotificationModuleConfig

from consumer_app.database import ConsumerDatabase
from consumer_app.notification_adapters import (
    InMemoryNotificationQueue,
    UnusedProviderResolver,
    UnusedTemplateRenderer,
)
from consumer_app.token_adapter import InMemoryAccessTokenAdapter


@dataclass(frozen=True, slots=True)
class ConsumerApplication:
    fastapi: FastAPI
    database: ConsumerDatabase
    notification: NotificationModule
    identity: IdentityModule
    notification_queue: InMemoryNotificationQueue
    token_adapter: InMemoryAccessTokenAdapter


async def build_consumer_application() -> ConsumerApplication:
    database = ConsumerDatabase()
    await database.create_schema()

    notification_queue = InMemoryNotificationQueue()
    notification = NotificationModule(
        NotificationModuleConfig(
            queue=notification_queue,
            renderer=UnusedTemplateRenderer(),
            provider_resolver=UnusedProviderResolver(),
        )
    )

    token_adapter = InMemoryAccessTokenAdapter()
    identity = IdentityModule(
        IdentityModuleConfig(
            session_factory=database.session_factory,
            notification_sender=notification.sender,
            access_token_issuer=token_adapter,
            access_token_authenticator=token_adapter,
            signing_secret=b"consumer-integration-signing-secret",
        )
    )

    fastapi = FastAPI()
    identity.fastapi.install(fastapi)

    return ConsumerApplication(
        fastapi=fastapi,
        database=database,
        notification=notification,
        identity=identity,
        notification_queue=notification_queue,
        token_adapter=token_adapter,
    )
