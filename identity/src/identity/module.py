from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import timedelta

from notification.public import NotificationSender

from identity.application.contracts.database import AsyncSessionFactory
from identity.application.contracts.rate_limiting import RateLimiter, RateLimitRule
from identity.application.contracts.security import AccessTokenIssuer
from identity.application.contracts.security_events import SecurityEventSink
from identity.application.factories.entities import (
    OtpChallengeFactory,
    SessionFactory,
    UserRegistrationFactory,
)
from identity.application.policies.data_retention import DataRetentionPolicy
from identity.application.policies.otp_purpose import OtpPurposePolicy
from identity.application.policies.otp_rate_limit import OtpRateLimitPolicy
from identity.application.policies.user_status import UserStatusPolicy
from identity.application.resolvers import VerifiedOtpUserResolver
from identity.application.services.cleanup_retained_data import CleanupRetainedIdentityDataService
from identity.application.services.refresh_session import RefreshSessionService
from identity.application.services.request_otp import RequestOtpService
from identity.application.services.revoke_all_sessions import RevokeAllSessionsService
from identity.application.services.revoke_session import RevokeSessionService
from identity.application.services.verify_otp import VerifyOtpService
from identity.application.verifiers import OtpChallengeVerifier
from identity.infrastructure.notifications import NotificationOtpDelivery
from identity.infrastructure.persistence.sqlalchemy.unit_of_work import (
    SqlAlchemyIdentityUnitOfWork,
    SqlAlchemyIdentityUnitOfWorkFactory,
)
from identity.infrastructure.security.hmac_digest import HmacSha256DigestCalculator
from identity.infrastructure.security.hmac_hash_format import HmacHashFormat
from identity.infrastructure.security.hmac_hasher import HmacSha256SecretHasher
from identity.infrastructure.security.hmac_key_validator import HmacKeyValidator
from identity.infrastructure.security.hmac_keyring import HmacKey, HmacKeyring
from identity.infrastructure.security.in_memory_rate_limiter import InMemoryRateLimiter
from identity.infrastructure.security.noop_security_event_sink import NoOpSecurityEventSink
from identity.infrastructure.security.normalizer import DefaultIdentityNormalizer
from identity.infrastructure.security.system_clock import SystemClock
from identity.infrastructure.security.token_generators import (
    SecureNumericOtpCodeGenerator,
    SecureRefreshTokenGenerator,
)
from identity.presentation.fastapi import FastApiIdentityAdapter
from identity.presentation.request_metadata import (
    DirectRequestMetadataResolver,
    RequestMetadataResolver,
)
from identity.public import AccessTokenAuthenticator, IdentityPublicApi


def _empty_signing_secrets() -> dict[str, bytes]:
    return {}


@dataclass(frozen=True, slots=True)
class IdentityModuleConfig:
    session_factory: AsyncSessionFactory
    notification_sender: NotificationSender
    access_token_issuer: AccessTokenIssuer
    access_token_authenticator: AccessTokenAuthenticator
    signing_secret: bytes
    signing_key_id: str = "v1"
    previous_signing_secrets: Mapping[str, bytes] = field(default_factory=_empty_signing_secrets)
    otp_ttl: timedelta = timedelta(minutes=5)
    otp_resend_delay: timedelta = timedelta(seconds=60)
    otp_max_attempts: int = 5
    session_ttl: timedelta = timedelta(days=30)
    session_absolute_ttl: timedelta = timedelta(days=90)
    otp_challenge_retention: timedelta = timedelta(days=7)
    session_retention: timedelta = timedelta(days=30)
    retention_cleanup_batch_size: int = 500
    rate_limiter: RateLimiter | None = None
    security_event_sink: SecurityEventSink | None = None
    request_metadata_resolver: RequestMetadataResolver | None = None
    otp_request_burst_limit: int = 5
    otp_request_burst_window: timedelta = timedelta(minutes=15)
    otp_request_daily_limit: int = 20
    otp_request_daily_window: timedelta = timedelta(days=1)
    otp_requester_burst_limit: int = 30
    otp_requester_burst_window: timedelta = timedelta(minutes=15)
    otp_verify_limit: int = 10
    otp_verify_window: timedelta = timedelta(minutes=1)
    otp_verify_requester_burst_limit: int = 60
    otp_verify_requester_burst_window: timedelta = timedelta(minutes=1)


class IdentityModule:
    def __init__(self, config: IdentityModuleConfig) -> None:
        self.config = config
        self._unit_of_work_factory = SqlAlchemyIdentityUnitOfWorkFactory(config.session_factory)
        clock = SystemClock()
        keyring = HmacKeyring(
            current_key=HmacKey(
                key_id=config.signing_key_id,
                secret=config.signing_secret,
            ),
            previous_keys=config.previous_signing_secrets,
            validator=HmacKeyValidator(),
        )
        hasher = HmacSha256SecretHasher(
            keyring=keyring,
            digest_calculator=HmacSha256DigestCalculator(),
            hash_format=HmacHashFormat(),
        )
        refresh_token_generator = SecureRefreshTokenGenerator()
        session_factory = SessionFactory(config.session_ttl, config.session_absolute_ttl)
        user_status_policy = UserStatusPolicy()
        rate_limiter = config.rate_limiter or InMemoryRateLimiter()
        security_event_sink = config.security_event_sink or NoOpSecurityEventSink()
        rate_limit_policy = OtpRateLimitPolicy(
            rate_limiter=rate_limiter,
            request_burst_rule=RateLimitRule(
                limit=config.otp_request_burst_limit,
                window=config.otp_request_burst_window,
            ),
            request_daily_rule=RateLimitRule(
                limit=config.otp_request_daily_limit,
                window=config.otp_request_daily_window,
            ),
            requester_burst_rule=RateLimitRule(
                limit=config.otp_requester_burst_limit,
                window=config.otp_requester_burst_window,
            ),
            verify_rule=RateLimitRule(
                limit=config.otp_verify_limit,
                window=config.otp_verify_window,
            ),
            verify_requester_rule=RateLimitRule(
                limit=config.otp_verify_requester_burst_limit,
                window=config.otp_verify_requester_burst_window,
            ),
        )
        otp_delivery = NotificationOtpDelivery(config.notification_sender)
        challenge_verifier = OtpChallengeVerifier(hasher)
        verified_user_resolver = VerifiedOtpUserResolver(
            registration_factory=UserRegistrationFactory(),
            user_status_policy=user_status_policy,
        )

        self.otp_requester = RequestOtpService(
            unit_of_work_factory=self._unit_of_work_factory,
            otp_delivery=otp_delivery,
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
            rate_limit_policy=rate_limit_policy,
            security_event_sink=security_event_sink,
        )
        self.otp_verifier = VerifyOtpService(
            unit_of_work_factory=self._unit_of_work_factory,
            clock=clock,
            hasher=hasher,
            refresh_token_generator=refresh_token_generator,
            access_token_issuer=config.access_token_issuer,
            session_factory=session_factory,
            challenge_verifier=challenge_verifier,
            user_resolver=verified_user_resolver,
            rate_limit_policy=rate_limit_policy,
            security_event_sink=security_event_sink,
        )
        self.session_refresher = RefreshSessionService(
            unit_of_work_factory=self._unit_of_work_factory,
            clock=clock,
            hasher=hasher,
            refresh_token_generator=refresh_token_generator,
            access_token_issuer=config.access_token_issuer,
            session_factory=session_factory,
            security_event_sink=security_event_sink,
        )
        self.session_revoker = RevokeSessionService(
            unit_of_work_factory=self._unit_of_work_factory,
            clock=clock,
            hasher=hasher,
            security_event_sink=security_event_sink,
        )
        self.session_bulk_revoker = RevokeAllSessionsService(
            unit_of_work_factory=self._unit_of_work_factory,
            clock=clock,
            security_event_sink=security_event_sink,
        )
        self.data_retention_cleaner = CleanupRetainedIdentityDataService(
            unit_of_work_factory=self._unit_of_work_factory,
            clock=clock,
            retention_policy=DataRetentionPolicy(
                otp_challenge_retention=config.otp_challenge_retention,
                session_retention=config.session_retention,
            ),
            batch_size=config.retention_cleanup_batch_size,
        )
        self.public_api = IdentityPublicApi(
            access_token_authenticator=config.access_token_authenticator,
            otp_requester=self.otp_requester,
            otp_verifier=self.otp_verifier,
            session_refresher=self.session_refresher,
            session_revoker=self.session_revoker,
            session_bulk_revoker=self.session_bulk_revoker,
            data_retention_cleaner=self.data_retention_cleaner,
        )
        self.fastapi = FastApiIdentityAdapter(
            access_token_authenticator=config.access_token_authenticator,
            otp_requester=self.otp_requester,
            otp_verifier=self.otp_verifier,
            session_refresher=self.session_refresher,
            session_revoker=self.session_revoker,
            session_bulk_revoker=self.session_bulk_revoker,
            request_metadata_resolver=(
                config.request_metadata_resolver or DirectRequestMetadataResolver()
            ),
        )

    @property
    def unit_of_work(self) -> SqlAlchemyIdentityUnitOfWork:
        return SqlAlchemyIdentityUnitOfWork(self.config.session_factory)
