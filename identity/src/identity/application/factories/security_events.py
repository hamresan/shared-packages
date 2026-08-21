from datetime import datetime
from uuid import UUID

from identity.application.contracts.security import SecretHasher
from identity.application.contracts.security_event_factory import SecurityEventFactory
from identity.application.contracts.security_events import SecurityEvent, SecurityEventName
from identity.domain import OtpChallenge, Session


class IdentitySecurityEventFactory(SecurityEventFactory):
    def __init__(self, hasher: SecretHasher) -> None:
        self._hasher = hasher

    def otp_request_rate_limited(
        self,
        *,
        occurred_at: datetime,
        destination: str,
    ) -> SecurityEvent:
        return SecurityEvent(
            name=SecurityEventName.OTP_REQUEST_RATE_LIMITED,
            occurred_at=occurred_at,
            subject_fingerprint=self._hasher.hash(destination),
        )

    def otp_verify_rate_limited(
        self,
        *,
        occurred_at: datetime,
        challenge_id: UUID,
    ) -> SecurityEvent:
        return SecurityEvent(
            name=SecurityEventName.OTP_VERIFY_RATE_LIMITED,
            occurred_at=occurred_at,
            challenge_id=challenge_id,
        )

    def otp_attempt_failed(
        self,
        *,
        occurred_at: datetime,
        challenge: OtpChallenge,
    ) -> SecurityEvent:
        return SecurityEvent(
            name=SecurityEventName.OTP_ATTEMPT_FAILED,
            occurred_at=occurred_at,
            user_id=challenge.user_id,
            challenge_id=challenge.id,
        )

    def otp_attempts_exceeded(
        self,
        *,
        occurred_at: datetime,
        challenge: OtpChallenge,
    ) -> SecurityEvent:
        return SecurityEvent(
            name=SecurityEventName.OTP_ATTEMPTS_EXCEEDED,
            occurred_at=occurred_at,
            user_id=challenge.user_id,
            challenge_id=challenge.id,
        )

    def refresh_reuse_detected(
        self,
        *,
        occurred_at: datetime,
        session: Session,
    ) -> SecurityEvent:
        return SecurityEvent(
            name=SecurityEventName.REFRESH_REUSE_DETECTED,
            occurred_at=occurred_at,
            user_id=session.user_id,
            session_id=session.id,
            family_id=session.family_id,
        )

    def session_revoked(
        self,
        *,
        occurred_at: datetime,
        session: Session,
    ) -> SecurityEvent:
        return SecurityEvent(
            name=SecurityEventName.SESSION_REVOKED,
            occurred_at=occurred_at,
            user_id=session.user_id,
            session_id=session.id,
            family_id=session.family_id,
        )

    def sessions_revoked_all(
        self,
        *,
        occurred_at: datetime,
        user_id: UUID,
    ) -> SecurityEvent:
        return SecurityEvent(
            name=SecurityEventName.SESSIONS_REVOKED_ALL,
            occurred_at=occurred_at,
            user_id=user_id,
        )
