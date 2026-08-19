from dataclasses import replace

from identity.application.contracts.security import (
    AccessTokenIssuer,
    Clock,
    RefreshTokenGenerator,
    SecretHasher,
)
from identity.application.contracts.security_events import (
    SecurityEvent,
    SecurityEventName,
    SecurityEventSink,
)
from identity.application.contracts.unit_of_work import IdentityUnitOfWorkFactory
from identity.application.dto import AuthSessionResult, VerifyOtpCommand
from identity.application.errors import (
    IdentityAlreadyRegisteredError,
    IdentityNotRegisteredError,
    IdentityRateLimitExceededError,
    InvalidOtpError,
    OtpAttemptsExceededError,
    OtpChallengeNotFoundError,
    OtpExpiredError,
    RegistrationNameRequiredError,
    UnsupportedOtpPurposeError,
)
from identity.application.factories.entities import SessionFactory, UserRegistrationFactory
from identity.application.policies.otp_rate_limit import OtpRateLimitPolicy
from identity.application.policies.user_status import UserStatusPolicy
from identity.domain import OtpPurpose


class VerifyOtpService:
    def __init__(
        self,
        *,
        unit_of_work_factory: IdentityUnitOfWorkFactory,
        clock: Clock,
        hasher: SecretHasher,
        refresh_token_generator: RefreshTokenGenerator,
        access_token_issuer: AccessTokenIssuer,
        registration_factory: UserRegistrationFactory,
        session_factory: SessionFactory,
        user_status_policy: UserStatusPolicy,
        rate_limit_policy: OtpRateLimitPolicy,
        security_event_sink: SecurityEventSink,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock
        self._hasher = hasher
        self._refresh_token_generator = refresh_token_generator
        self._access_token_issuer = access_token_issuer
        self._registration_factory = registration_factory
        self._session_factory = session_factory
        self._user_status_policy = user_status_policy
        self._rate_limit_policy = rate_limit_policy
        self._security_event_sink = security_event_sink

    async def execute(self, command: VerifyOtpCommand) -> AuthSessionResult:
        now = self._clock.now()
        try:
            await self._rate_limit_policy.ensure_verification_allowed(command.challenge_id, now)
        except IdentityRateLimitExceededError:
            await self._security_event_sink.emit(
                SecurityEvent(
                    name=SecurityEventName.OTP_VERIFY_RATE_LIMITED,
                    occurred_at=now,
                    challenge_id=command.challenge_id,
                )
            )
            raise

        async with self._unit_of_work_factory() as uow:
            challenge = await uow.otp_challenges.get_for_update(command.challenge_id)
            if challenge is None or challenge.consumed_at is not None:
                raise OtpChallengeNotFoundError("OTP challenge was not found")
            if challenge.expires_at <= now:
                raise OtpExpiredError("OTP challenge has expired")
            if challenge.attempts_count >= challenge.max_attempts:
                await self._security_event_sink.emit(
                    SecurityEvent(
                        name=SecurityEventName.OTP_ATTEMPTS_EXCEEDED,
                        occurred_at=now,
                        user_id=challenge.user_id,
                        challenge_id=challenge.id,
                    )
                )
                raise OtpAttemptsExceededError("OTP attempts exceeded")
            if not self._hasher.verify(command.code, challenge.code_hash):
                await uow.otp_challenges.increment_attempts(challenge.id)
                await uow.commit()
                await self._security_event_sink.emit(
                    SecurityEvent(
                        name=SecurityEventName.OTP_ATTEMPT_FAILED,
                        occurred_at=now,
                        user_id=challenge.user_id,
                        challenge_id=challenge.id,
                    )
                )
                raise InvalidOtpError("OTP code is invalid")

            if challenge.purpose is OtpPurpose.REGISTRATION:
                if challenge.user_id is not None:
                    raise IdentityAlreadyRegisteredError("Identity is already registered")
                if not command.full_name or not command.full_name.strip():
                    raise RegistrationNameRequiredError("Full name is required for registration")
                user, identity = self._registration_factory.create(
                    now=now,
                    full_name=command.full_name.strip(),
                    identity_type=challenge.identifier_type,
                    destination=challenge.normalized_destination,
                )
                await uow.users.add(user)
                await uow.identities.add(identity)
            elif challenge.purpose is OtpPurpose.LOGIN:
                if challenge.user_id is None:
                    raise IdentityNotRegisteredError("Identity is not registered")
                user = await uow.users.get(challenge.user_id)
                if user is None:
                    raise OtpChallengeNotFoundError("OTP challenge user was not found")
                self._user_status_policy.ensure_active(user)
            else:
                raise UnsupportedOtpPurposeError(
                    f"OTP purpose is not supported: {challenge.purpose.value}"
                )

            refresh_token = self._refresh_token_generator.generate()
            session = self._session_factory.create(
                now=now,
                user_id=user.id,
                refresh_token_hash=self._hasher.hash(refresh_token),
                device_info=command.device_info,
                ip_address=command.ip_address,
            )
            access_token = await self._access_token_issuer.issue(user.id, session.id)
            await uow.sessions.add(session)
            await uow.otp_challenges.save(replace(challenge, verified_at=now, consumed_at=now))
            await uow.commit()

        return AuthSessionResult(
            user_id=user.id,
            session_id=session.id,
            access_token=access_token.token,
            access_token_expires_at=access_token.expires_at,
            refresh_token=refresh_token,
            refresh_token_expires_at=session.expires_at,
        )
