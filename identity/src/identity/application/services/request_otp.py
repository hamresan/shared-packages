from identity.application.contracts.otp_delivery import OtpDelivery
from identity.application.contracts.security import (
    Clock,
    IdentityNormalizer,
    OtpCodeGenerator,
    SecretHasher,
)
from identity.application.contracts.security_event_factory import SecurityEventFactory
from identity.application.contracts.security_events import SecurityEventSink
from identity.application.contracts.unit_of_work import IdentityUnitOfWorkFactory
from identity.application.dto import RequestOtpCommand, RequestOtpResult
from identity.application.errors import IdentityRateLimitExceededError
from identity.application.factories.entities import OtpChallengeFactory
from identity.application.policies.otp_purpose import OtpPurposePolicy
from identity.application.policies.otp_rate_limit import OtpRateLimitPolicy


class RequestOtpService:
    def __init__(
        self,
        *,
        unit_of_work_factory: IdentityUnitOfWorkFactory,
        otp_delivery: OtpDelivery,
        clock: Clock,
        normalizer: IdentityNormalizer,
        code_generator: OtpCodeGenerator,
        hasher: SecretHasher,
        challenge_factory: OtpChallengeFactory,
        purpose_policy: OtpPurposePolicy,
        rate_limit_policy: OtpRateLimitPolicy,
        security_event_sink: SecurityEventSink,
        security_event_factory: SecurityEventFactory,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._otp_delivery = otp_delivery
        self._clock = clock
        self._normalizer = normalizer
        self._code_generator = code_generator
        self._hasher = hasher
        self._challenge_factory = challenge_factory
        self._purpose_policy = purpose_policy
        self._rate_limit_policy = rate_limit_policy
        self._security_event_sink = security_event_sink
        self._security_event_factory = security_event_factory

    async def execute(self, command: RequestOtpCommand) -> RequestOtpResult:
        now = self._clock.now()
        destination = self._normalizer.normalize(command.identity_type, command.destination)
        self._purpose_policy.validate(command.purpose)

        try:
            await self._rate_limit_policy.ensure_requester_allowed(command.ip_address, now)
        except IdentityRateLimitExceededError:
            await self._security_event_sink.emit(
                self._security_event_factory.otp_request_rate_limited(
                    occurred_at=now,
                    destination=destination,
                )
            )
            raise

        async with self._unit_of_work_factory() as uow:
            identity = await uow.identities.get_by_destination(command.identity_type, destination)
            self._purpose_policy.validate_identity_state(
                command.purpose,
                is_registered=identity is not None,
            )
            latest = await uow.otp_challenges.get_latest_active(
                destination,
                command.purpose,
                now,
            )
            if latest is not None and latest.resend_available_at > now:
                return RequestOtpResult(
                    challenge_id=latest.id,
                    expires_at=latest.expires_at,
                    resend_available_at=latest.resend_available_at,
                )

            try:
                await self._rate_limit_policy.ensure_destination_request_allowed(destination, now)
            except IdentityRateLimitExceededError:
                await self._security_event_sink.emit(
                    self._security_event_factory.otp_request_rate_limited(
                        occurred_at=now,
                        destination=destination,
                    )
                )
                raise

            code = self._code_generator.generate()
            challenge = self._challenge_factory.create(
                now=now,
                identity_type=command.identity_type,
                destination=destination,
                purpose=command.purpose,
                code_hash=self._hasher.hash(code),
                user_id=identity.user_id if identity else None,
                identity_id=identity.id if identity else None,
            )
            await uow.otp_challenges.add(challenge)
            await self._otp_delivery.send(
                identity_type=command.identity_type,
                destination=destination,
                code=code,
                purpose=command.purpose,
                locale=command.locale,
            )
            await uow.commit()

        return RequestOtpResult(
            challenge_id=challenge.id,
            expires_at=challenge.expires_at,
            resend_available_at=challenge.resend_available_at,
        )
