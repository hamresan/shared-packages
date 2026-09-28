from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from identity.domain import IdentityType, OtpPurpose


@dataclass(frozen=True, slots=True)
class RequestOtpCommand:
    identity_type: IdentityType
    destination: str
    purpose: OtpPurpose
    locale: str = "en"
    ip_address: str | None = None


@dataclass(frozen=True, slots=True)
class RequestOtpResult:
    challenge_id: UUID
    expires_at: datetime
    resend_available_at: datetime


@dataclass(frozen=True, slots=True)
class VerifyOtpCommand:
    challenge_id: UUID
    code: str
    full_name: str | None = None
    device_info: str | None = None
    ip_address: str | None = None


@dataclass(frozen=True, slots=True)
class AuthSessionResult:
    user_id: UUID
    session_id: UUID
    access_token: str
    access_token_expires_at: datetime
    refresh_token: str
    refresh_token_expires_at: datetime
    purpose: OtpPurpose


@dataclass(frozen=True, slots=True)
class RefreshSessionCommand:
    refresh_token: str
    device_info: str | None = None
    ip_address: str | None = None


@dataclass(frozen=True, slots=True)
class DataRetentionCleanupResult:
    deleted_otp_challenges: int
    deleted_sessions: int
