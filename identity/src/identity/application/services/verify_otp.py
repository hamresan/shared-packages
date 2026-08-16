from dataclasses import replace

from identity.application.contracts.security import (
    AccessTokenIssuer,
    Clock,
    RefreshTokenGenerator,
    SecretHasher,
)
from identity.application.contracts.unit_of_work import IdentityUnitOfWorkFactory
from identity.application.dto import AuthSessionResult, VerifyOtpCommand
from identity.application.errors import (
    InvalidOtpError,
    OtpAttemptsExceededError,
    OtpChallengeNotFoundError,
    OtpExpiredError,
    RegistrationNameRequiredError,
)
from identity.application.factories.entities import SessionFactory, UserRegistrationFactory
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
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock
        self._hasher = hasher
        self._refresh_token_generator = refresh_token_generator
        self._access_token_issuer = access_token_issuer
        self._registration_factory = registration_factory
        self._session_factory = session_factory

    async def execute(self, command: VerifyOtpCommand) -> AuthSessionResult:
        now = self._clock.now()
        async with self._unit_of_work_factory() as uow:
            challenge = await uow.otp_challenges.get(command.challenge_id)
            if challenge is None or challenge.consumed_at is not None:
                raise OtpChallengeNotFoundError("OTP challenge was not found")
            if challenge.expires_at <= now:
                raise OtpExpiredError("OTP challenge has expired")
            if challenge.attempts_count >= challenge.max_attempts:
                raise OtpAttemptsExceededError("OTP attempts exceeded")
            if not self._hasher.verify(command.code, challenge.code_hash):
                await uow.otp_challenges.save(
                    replace(challenge, attempts_count=challenge.attempts_count + 1)
                )
                await uow.commit()
                raise InvalidOtpError("OTP code is invalid")

            if challenge.purpose is OtpPurpose.REGISTRATION:
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
            else:
                if challenge.user_id is None:
                    raise OtpChallengeNotFoundError("OTP challenge has no user")
                user = await uow.users.get(challenge.user_id)
                if user is None:
                    raise OtpChallengeNotFoundError("OTP challenge user was not found")

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
