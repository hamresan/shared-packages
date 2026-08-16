from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from identity.application.contracts.security import AccessTokenIssuer, IssuedAccessToken
from identity.application.dto import (
    AuthSessionResult,
    RefreshSessionCommand,
    RequestOtpCommand,
    RequestOtpResult,
    VerifyOtpCommand,
)
from identity.public.services import OtpRequester, OtpVerifier, SessionRefresher, SessionRevoker


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    user_id: UUID
    session_id: UUID
    authentication_method: str
    issued_at: datetime
    expires_at: datetime
    permissions: frozenset[str] = frozenset()


class AccessTokenAuthenticator(Protocol):
    async def authenticate(self, access_token: str) -> AuthenticatedPrincipal: ...


@dataclass(frozen=True, slots=True)
class IdentityPublicApi:
    access_token_authenticator: AccessTokenAuthenticator
    otp_requester: OtpRequester
    otp_verifier: OtpVerifier
    session_refresher: SessionRefresher
    session_revoker: SessionRevoker


__all__ = [
    "AccessTokenAuthenticator",
    "AccessTokenIssuer",
    "AuthSessionResult",
    "AuthenticatedPrincipal",
    "IdentityPublicApi",
    "IssuedAccessToken",
    "OtpRequester",
    "OtpVerifier",
    "RefreshSessionCommand",
    "RequestOtpCommand",
    "RequestOtpResult",
    "SessionRefresher",
    "SessionRevoker",
    "VerifyOtpCommand",
]
