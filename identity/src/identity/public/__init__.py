from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from identity.application.contracts.security import AccessTokenIssuer, IssuedAccessToken
from identity.application.dto import (
    AuthSessionResult,
    DataRetentionCleanupResult,
    RefreshSessionCommand,
    RequestOtpCommand,
    RequestOtpResult,
    VerifyOtpCommand,
)
from identity.domain import IdentityType, OtpPurpose
from identity.public.errors import AccessTokenAuthenticationError
from identity.public.services import (
    IdentityDataRetentionCleaner,
    OtpRequester,
    OtpVerifier,
    SessionBulkRevoker,
    SessionRefresher,
    SessionRevoker,
)


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    user_id: UUID
    session_id: UUID
    authentication_method: str
    issued_at: datetime
    expires_at: datetime


class AccessTokenAuthenticator(Protocol):
    async def authenticate(self, access_token: str) -> AuthenticatedPrincipal: ...


@dataclass(frozen=True, slots=True)
class IdentityPublicApi:
    access_token_authenticator: AccessTokenAuthenticator
    otp_requester: OtpRequester
    otp_verifier: OtpVerifier
    session_refresher: SessionRefresher
    session_revoker: SessionRevoker
    session_bulk_revoker: SessionBulkRevoker
    data_retention_cleaner: IdentityDataRetentionCleaner


__all__ = [
    "AccessTokenAuthenticationError",
    "AccessTokenAuthenticator",
    "AccessTokenIssuer",
    "AuthSessionResult",
    "AuthenticatedPrincipal",
    "DataRetentionCleanupResult",
    "IdentityDataRetentionCleaner",
    "IdentityPublicApi",
    "IdentityType",
    "IssuedAccessToken",
    "OtpPurpose",
    "OtpRequester",
    "OtpVerifier",
    "RefreshSessionCommand",
    "RequestOtpCommand",
    "RequestOtpResult",
    "SessionBulkRevoker",
    "SessionRefresher",
    "SessionRevoker",
    "VerifyOtpCommand",
]
