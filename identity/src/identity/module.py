from dataclasses import dataclass
from datetime import timedelta

from notification.public import NotificationSender

from identity.application.contracts.database import AsyncSessionFactory
from identity.application.contracts.security import AccessTokenIssuer
from identity.application.factories.entities import (
    OtpChallengeFactory,
    SessionFactory,
    UserRegistrationFactory,
)
from identity.application.policies.otp_purpose import OtpPurposePolicy
from identity.application.policies.user_status import UserStatusPolicy
from identity.application.services.refresh_session import RefreshSessionService
from identity.application.services.request_otp import RequestOtpService
from identity.application.services.revoke_session import RevokeSessionService
from identity.application.services.verify_otp import VerifyOtpService
from identity.infrastructure.persistence.sqlalchemy.unit_of_work import (
    SqlAlchemyIdentityUnitOfWork,
    SqlAlchemyIdentityUnitOfWorkFactory,
)
from identity.infrastructure.security.hmac_hasher import HmacSha256SecretHasher
from identity.infrastructure.security.normalizer import DefaultIdentityNormalizer
from identity.infrastructure.security.system_clock import SystemClock
from identity.infrastructure.security.token_generators import (
    SecureNumericOtpCodeGenerator,
    SecureRefreshTokenGenerator,
)
from identity.presentation.fastapi import FastApiIdentityAdapter
from identity.public import AccessTokenAuthenticator, IdentityPublicApi


@dataclass(frozen=True, slots=True)
class IdentityModuleConfig:
    session_factory: AsyncSessionFactory
    notification_sender: NotificationSender
    access_token_issuer: AccessTokenIssuer
    access_token_authenticator: AccessTokenAuthenticator
    signing_secret: bytes
    otp_ttl: timedelta = timedelta(minutes=5)
    otp_resend_delay: timedelta = timedelta(seconds=60)
    otp_max_attempts: int = 5
    session_ttl: timedelta = timedelta(days=30)
    session_absolute_ttl: timedelta = timedelta(days=90)


class IdentityModule:
    def __init__(self, config: IdentityModuleConfig) -> None:
        self.config = config
        self._unit_of_work_factory = SqlAlchemyIdentityUnitOfWorkFactory(config.session_factory)
        clock = SystemClock()
        hasher = HmacSha256SecretHasher(config.signing_secret)
        refresh_token_generator = SecureRefreshTokenGenerator()
        session_factory = SessionFactory(config.session_ttl, config.session_absolute_ttl)
        user_status_policy = UserStatusPolicy()

        self.otp_requester = RequestOtpService(
            unit_of_work_factory=self._unit_of_work_factory,
            notification_sender=config.notification_sender,
            clock=clock,
            normalizer=DefaultIdentityNormalizer(),
            code_generator=SecureNumericOtpCodeGenerator(),
            hasher=hasher,
            challenge_factory=OtpChallengeFactory(
                ttl=config.otp_ttl,
                resend_delay=config.otp_resend_delay,
                max_attempts=config.otp_max_attempts,
            ),
            purpose_policy=OtpPurposePolicy(),
        )
        self.otp_verifier = VerifyOtpService(
            unit_of_work_factory=self._unit_of_work_factory,
            clock=clock,
            hasher=hasher,
            refresh_token_generator=refresh_token_generator,
            access_token_issuer=config.access_token_issuer,
            registration_factory=UserRegistrationFactory(),
            session_factory=session_factory,
            user_status_policy=user_status_policy,
        )
        self.session_refresher = RefreshSessionService(
            unit_of_work_factory=self._unit_of_work_factory,
            clock=clock,
            hasher=hasher,
            refresh_token_generator=refresh_token_generator,
            access_token_issuer=config.access_token_issuer,
            session_factory=session_factory,
        )
        self.session_revoker = RevokeSessionService(
            unit_of_work_factory=self._unit_of_work_factory,
            clock=clock,
            hasher=hasher,
        )
        self.public_api = IdentityPublicApi(
            access_token_authenticator=config.access_token_authenticator,
            otp_requester=self.otp_requester,
            otp_verifier=self.otp_verifier,
            session_refresher=self.session_refresher,
            session_revoker=self.session_revoker,
        )
        self.fastapi = FastApiIdentityAdapter(
            access_token_authenticator=config.access_token_authenticator,
            otp_requester=self.otp_requester,
            otp_verifier=self.otp_verifier,
            session_refresher=self.session_refresher,
            session_revoker=self.session_revoker,
        )

    @property
    def unit_of_work(self) -> SqlAlchemyIdentityUnitOfWork:
        return SqlAlchemyIdentityUnitOfWork(self.config.session_factory)
