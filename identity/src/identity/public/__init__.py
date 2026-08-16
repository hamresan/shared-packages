from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID


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


__all__ = [
    "AccessTokenAuthenticator",
    "AuthenticatedPrincipal",
    "IdentityPublicApi",
]
