from datetime import datetime
from typing import Protocol
from uuid import UUID

from identity.application.contracts.security_events import SecurityEvent
from identity.domain import OtpChallenge, Session


class SecurityEventFactory(Protocol):
    def otp_request_rate_limited(
        self,
        *,
        occurred_at: datetime,
        destination: str,
    ) -> SecurityEvent: ...

    def otp_verify_rate_limited(
        self,
        *,
        occurred_at: datetime,
        challenge_id: UUID,
    ) -> SecurityEvent: ...

    def otp_attempt_failed(
        self,
        *,
        occurred_at: datetime,
        challenge: OtpChallenge,
    ) -> SecurityEvent: ...

    def otp_attempts_exceeded(
        self,
        *,
        occurred_at: datetime,
        challenge: OtpChallenge,
    ) -> SecurityEvent: ...

    def refresh_reuse_detected(
        self,
        *,
        occurred_at: datetime,
        session: Session,
    ) -> SecurityEvent: ...

    def session_revoked(
        self,
        *,
        occurred_at: datetime,
        session: Session,
    ) -> SecurityEvent: ...

    def sessions_revoked_all(
        self,
        *,
        occurred_at: datetime,
        user_id: UUID,
    ) -> SecurityEvent: ...
