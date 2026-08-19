from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class SecurityEventName(StrEnum):
    OTP_REQUEST_RATE_LIMITED = "otp.request_rate_limited"
    OTP_VERIFY_RATE_LIMITED = "otp.verify_rate_limited"
    OTP_ATTEMPT_FAILED = "otp.attempt_failed"
    OTP_ATTEMPTS_EXCEEDED = "otp.attempts_exceeded"
    REFRESH_REUSE_DETECTED = "refresh.reuse_detected"
    SESSION_REVOKED = "session.revoked"
    SESSIONS_REVOKED_ALL = "session.revoked_all"


@dataclass(frozen=True, slots=True)
class SecurityEvent:
    name: SecurityEventName
    occurred_at: datetime
    user_id: UUID | None = None
    session_id: UUID | None = None
    family_id: UUID | None = None
    challenge_id: UUID | None = None
    subject_fingerprint: str | None = None


class SecurityEventSink(Protocol):
    async def emit(self, event: SecurityEvent) -> None: ...
