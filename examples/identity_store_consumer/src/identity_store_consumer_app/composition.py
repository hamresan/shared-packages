from dataclasses import dataclass

from fastapi import FastAPI
from identity import IdentityModule, IdentityModuleConfig
from store.presentation import FastApiStoreAdapter

from identity_store_consumer_app.authentication import (
    IdentityStoreActorDependency,
    InMemoryAccessTokenAdapter,
)
from identity_store_consumer_app.database import ConsumerDatabase
from identity_store_consumer_app.notification import NullNotificationSender
from identity_store_consumer_app.settings import ConsumerSettings, load_consumer_settings
from identity_store_consumer_app.store_runtime import build_store_adapter


@dataclass(frozen=True, slots=True)
class ConsumerApplication:
    fastapi: FastAPI
    database: ConsumerDatabase
    identity: IdentityModule
    store: FastApiStoreAdapter
    token_adapter: InMemoryAccessTokenAdapter


async def build_consumer_application(
    settings: ConsumerSettings | None = None,
) -> ConsumerApplication:
    application_settings = settings or load_consumer_settings()
    database = ConsumerDatabase()
    await database.create_schema()

    token_adapter = InMemoryAccessTokenAdapter()
    identity = IdentityModule(
        IdentityModuleConfig(
            session_factory=database.session_factory,
            notification_sender=NullNotificationSender(),
            access_token_issuer=token_adapter,
            access_token_authenticator=token_adapter,
            signing_secret=application_settings.identity_signing_secret,
        )
    )
    store = build_store_adapter(
        database,
        IdentityStoreActorDependency(identity.public_api.access_token_authenticator),
    )

    fastapi = FastAPI()
    identity.fastapi.install(fastapi)
    store.install(fastapi)

    return ConsumerApplication(
        fastapi=fastapi,
        database=database,
        identity=identity,
        store=store,
        token_adapter=token_adapter,
    )
