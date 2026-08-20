from notification.public import NotificationChannel, NotificationSender, SendNotification

from identity.application.contracts.security import (
    Clock,
    IdentityNormalizer,
    OtpCodeGenerator,
    SecretHasher,
)
from identity.application.contracts.security_events import (
    SecurityEvent,
    SecurityEventName,
    SecurityEventSink,
)
from identity.application.contracts.unit_of_work import IdentityUnitOfWorkFactory
from identity.application.dto import RequestOtpCommand, RequestOtpResult
from identity.application.errors import IdentityRateLimitExceededError
from identity.application.factories.entities import OtpChallengeFactory
from identity.application.policies.otp_purpose import OtpPurposePolicy
from identity.application.policies.otp_rate_limit import OtpRateLimitPolicy
from identity.domain import IdentityType


class RequestOtpService:
    def __init__(
        self,
        *,
        unit_of_work_factory: IdentityUnitOfWorkFactory,
        notification_sender: NotificationSender,
        clock: Clock,
        normalizer: IdentityNormalizer,
        code_generator: OtpCodeGenerator,
        hasher: SecretHasher,
        challenge_factory: OtpChallengeFactory,
        purpose_policy: OtpPurposePolicy,
        rate_limit_policy: OtpRateLimitPolicy,
        security_event_sink: SecurityEventSink,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._notification_sender = notification_sender
        self._clock = clock
        self._normalizer = normalizer
        self._code_generator = code_generator
        self._hasher = hasher
        self._challenge_factory = challenge_factory
        self._purpose_policy = purpose_policy
        self._rate_limit_policy = rate_limit_policy
        self._security_event_sink = security_event_sink

    async def execute(self, command: RequestOtpCommand) -> RequestOtpResult:
        now = self._clock.now()
        destination = self._normalizer.normalize(command.identity_type, command.destination)
        try:
            await self._rate_limit_policy.ensure_request_allowed(
                destination,
                command.ip_address,
                now,
            )
        except IdentityRateLimitExceededError:
            await self._security_event_sink.emit(
                SecurityEvent(
                    name=SecurityEventName.OTP_REQUEST_RATE_LIMITED,
                    occurred_at=now,
                    subject_fingerprint=self._hasher.hash(destination),
                )
            )
            raise
        self._purpose_policy.validate(command.purpose)

        channel = (
            NotificationChannel.SMS
            if command.identity_type is IdentityType.MOBILE
            else NotificationChannel.EMAIL
        )

        async with self._unit_of_work_factory() as uow:
            identity = await uow.identities.get_by_destination(command.identity_type, destination)
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
            await self._notification_sender.send(
                SendNotification(
                    channel=channel,
                    recipient=destination,
                    template_key="identity.otp",
                    locale=command.locale,
                    variables={"otp": code, "purpose": command.purpose.value},
                )
            )
            await uow.commit()

        return RequestOtpResult(
            challenge_id=challenge.id,
            expires_at=challenge.expires_at,
            resend_available_at=challenge.resend_available_at,
        )
