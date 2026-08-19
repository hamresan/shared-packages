from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class UserStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISABLED = "disabled"


class IdentityType(StrEnum):
    MOBILE = "mobile"
    EMAIL = "email"


class OtpPurpose(StrEnum):
    REGISTRATION = "registration"
    LOGIN = "login"
    VERIFY_EMAIL = "verify_email"
    CHANGE_EMAIL = "change_email"
    CHANGE_MOBILE = "change_mobile"
    ACCOUNT_RECOVERY = "account_recovery"


@dataclass(frozen=True, slots=True)
class User:
    id: UUID
    full_name: str
    status: UserStatus
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class UserIdentity:
    id: UUID
    user_id: UUID
    type: IdentityType
    value: str
    normalized_value: str
    verified_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class OtpChallenge:
    id: UUID
    user_id: UUID | None
    identity_id: UUID | None
    identifier_type: IdentityType
    normalized_destination: str
    destination_snapshot: str
    purpose: OtpPurpose
    code_hash: str
    expires_at: datetime
    resend_available_at: datetime
    attempts_count: int
    max_attempts: int
    verified_at: datetime | None
    consumed_at: datetime | None
    created_at: datetime


@dataclass(frozen=True, slots=True)
class Session:
    id: UUID
    user_id: UUID
    refresh_token_hash: str
    family_id: UUID
    parent_session_id: UUID | None
    replaced_by_session_id: UUID | None
    expires_at: datetime
    family_expires_at: datetime
    revoked_at: datetime | None
    device_info: str | None
    ip_address: str | None
    created_at: datetime
    last_used_at: datetime | None
