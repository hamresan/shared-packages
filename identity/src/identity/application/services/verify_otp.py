from dataclasses import replace

from identity.application.contracts.security import (
    AccessTokenIssuer,
    Clock,
    RefreshTokenGenerator,
    SecretHasher,
)
from identity.application.contracts.security_event_factory import SecurityEventFactory
from identity.application.contracts.security_events import SecurityEventSink
from identity.application.contracts.unit_of_work import IdentityUnitOfWorkFactory
from identity.application.dto import AuthSessionResult, VerifyOtpCommand
from identity.application.errors import (
    IdentityRateLimitExceededError,
    InvalidOtpError,
    OtpAttemptsExceededError,
)
from identity.application.factories.entities import SessionFactory
from identity.application.policies.otp_rate_limit import OtpRateLimitPolicy
from identity.application.resolvers import VerifiedOtpUserResolver
from identity.application.verifiers import OtpChallengeVerifier


class VerifyOtpService:
    def __init__(
        self,
        *,
        unit_of_work_factory: IdentityUnitOfWorkFactory,
        clock: Clock,
        hasher: SecretHasher,
        refresh_token_generator: RefreshTokenGenerator,
        access_token_issuer: AccessTokenIssuer,
        session_factory: SessionFactory,
        challenge_verifier: OtpChallengeVerifier,
        user_resolver: VerifiedOtpUserResolver,
        rate_limit_policy: OtpRateLimitPolicy,
        security_event_sink: SecurityEventSink,
        security_event_factory: SecurityEventFactory,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock
        self._hasher = hasher
        self._refresh_token_generator = refresh_token_generator
        self._access_token_issuer = access_token_issuer
        self._session_factory = session_factory
        self._challenge_verifier = challenge_verifier
        self._user_resolver = user_resolver
        self._rate_limit_policy = rate_limit_policy
        self._security_event_sink = security_event_sink
        self._security_event_factory = security_event_factory

    async def execute(self, command: VerifyOtpCommand) -> AuthSessionResult:
        now = self._clock.now()
        try:
            await self._rate_limit_policy.ensure_verification_allowed(
                command.challenge_id,
                command.ip_address,
                now,
            )
        except IdentityRateLimitExceededError:
            await self._security_event_sink.emit(
                self._security_event_factory.otp_verify_rate_limited(
                    occurred_at=now,
                    challenge_id=command.challenge_id,
                )
            )
            raise

        async with self._unit_of_work_factory() as uow:
            challenge = await uow.otp_challenges.get_for_update(command.challenge_id)
            try:
                verified_challenge = self._challenge_verifier.verify(
                    challenge=challenge,
                    code=command.code,
                    now=now,
                )
            except OtpAttemptsExceededError:
                if challenge is not None:
                    await self._security_event_sink.emit(
                        self._security_event_factory.otp_attempts_exceeded(
                            occurred_at=now,
                            challenge=challenge,
                        )
                    )
                raise
            except InvalidOtpError:
                if challenge is not None:
                    await uow.otp_challenges.increment_attempts(challenge.id)
                    await uow.commit()
                    await self._security_event_sink.emit(
                        self._security_event_factory.otp_attempt_failed(
                            occurred_at=now,
                            challenge=challenge,
                        )
                    )
                raise

            user = await self._user_resolver.resolve(
                users=uow.users,
                identities=uow.identities,
                challenge=verified_challenge,
                full_name=command.full_name,
                now=now,
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
            await uow.otp_challenges.save(
                replace(verified_challenge, verified_at=now, consumed_at=now)
            )
            await uow.commit()

        return AuthSessionResult(
            user_id=user.id,
            session_id=session.id,
            access_token=access_token.token,
            access_token_expires_at=access_token.expires_at,
            refresh_token=refresh_token,
            refresh_token_expires_at=session.expires_at,
            purpose=verified_challenge.purpose,
        )
