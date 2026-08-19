from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from identity.domain import IdentityType, OtpPurpose

SupportedOtpPurpose = Literal[OtpPurpose.REGISTRATION, OtpPurpose.LOGIN]


class RequestOtpRequest(BaseModel):
    identity_type: IdentityType
    destination: str = Field(min_length=3, max_length=320)
    purpose: SupportedOtpPurpose
    locale: str = Field(default="en", min_length=2, max_length=16)


class RequestOtpResponse(BaseModel):
    challenge_id: UUID
    expires_at: datetime
    resend_available_at: datetime


class VerifyOtpRequest(BaseModel):
    challenge_id: UUID
    code: str = Field(min_length=4, max_length=12)
    full_name: str | None = Field(default=None, max_length=160)
    device_info: str | None = Field(default=None, max_length=512)
    ip_address: str | None = Field(default=None, max_length=64)


class AuthSessionResponse(BaseModel):
    user_id: UUID
    session_id: UUID
    access_token: str
    access_token_expires_at: datetime
    refresh_token: str
    refresh_token_expires_at: datetime


class RefreshSessionRequest(BaseModel):
    refresh_token: str = Field(min_length=32)
    device_info: str | None = Field(default=None, max_length=512)
    ip_address: str | None = Field(default=None, max_length=64)


class RevokeSessionRequest(BaseModel):
    refresh_token: str = Field(min_length=32)
