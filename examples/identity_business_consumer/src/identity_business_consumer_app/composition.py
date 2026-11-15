from dataclasses import dataclass
from datetime import timedelta

from business.bootstrap import BusinessApplicationFactory
from business.infrastructure.clock import SystemClock as BusinessClock
from business.infrastructure.identifiers import UuidIdentifierGenerator
from business.infrastructure.persistence.sqlalchemy import (
    BranchMapper,
    BusinessMapper,
    MembershipAuditMapper,
    MembershipMapper,
    SqlAlchemyBusinessUnitOfWorkFactory,
)
from business.presentation import build_fastapi_business_adapter
from fastapi import FastAPI
from identity import IdentityModule, IdentityModuleConfig
from identity.access_tokens import (
    JwtAccessTokenAuthenticator,
    JwtAccessTokenIssuer,
    PyJwtHmacCodec,
    SqlAlchemySessionReader,
    SqlAlchemyUserReader,
    UserStatusPolicy,
)
from identity.infrastructure.security.system_clock import SystemClock as IdentityClock
from notification import NotificationModule, NotificationModuleConfig

from identity_business_consumer_app.authentication import IdentityBusinessActorDependency
from identity_business_consumer_app.database import ConsumerDatabase
from identity_business_consumer_app.notifications import (
    CapturingNotificationQueue,
    UnusedProviderResolver,
    UnusedTemplateRenderer,
)


@dataclass(frozen=True, slots=True)
class ConsumerApplication:
    fastapi: FastAPI
    database: ConsumerDatabase
    identity: IdentityModule
    notification_queue: CapturingNotificationQueue


async def build_consumer_application(*, signing_secret: str) -> ConsumerApplication:
    """Compose real Identity OTP/JWT, Notification and Business in one host."""
    database = ConsumerDatabase()
    await database.create_schema()
    queue = CapturingNotificationQueue()
    notification = NotificationModule(
        NotificationModuleConfig(
            queue=queue,
            renderer=UnusedTemplateRenderer(),
            provider_resolver=UnusedProviderResolver(),
        )
    )

    codec = PyJwtHmacCodec(signing_secret)
    identity_clock = IdentityClock()
    issuer = JwtAccessTokenIssuer(codec, identity_clock, timedelta(minutes=15))
    authenticator = JwtAccessTokenAuthenticator(
        codec,
        SqlAlchemySessionReader(database.session_factory),
        SqlAlchemyUserReader(database.session_factory),
        UserStatusPolicy(),
        identity_clock,
    )
    identity = IdentityModule(
        IdentityModuleConfig(
            session_factory=database.session_factory,
            notification_sender=notification.sender,
            access_token_issuer=issuer,
            access_token_authenticator=authenticator,
            signing_secret=signing_secret.encode("utf-8"),
        )
    )

    business_uow = SqlAlchemyBusinessUnitOfWorkFactory(
        database.session_maker,
        BusinessMapper(),
        BranchMapper(),
        MembershipMapper(),
        MembershipAuditMapper(),
    )
    use_cases = BusinessApplicationFactory(business_uow, BusinessClock(), UuidIdentifierGenerator())
    business_adapter = build_fastapi_business_adapter(
        authenticated_actor_dependency=IdentityBusinessActorDependency(
            identity.public_api.access_token_authenticator
        ),
        businesses=use_cases.businesses(),
        branches=use_cases.branches(),
        memberships=use_cases.memberships(),
    )

    app = FastAPI()
    identity.fastapi.install(app)
    business_adapter.install(app)
    return ConsumerApplication(app, database, identity, queue)
