from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AccessTokenClaims:
    user_id: UUID
    session_id: UUID
    issued_at: datetime
    expires_at: datetime


class TokenSigner(Protocol):
    def sign(self, claims: AccessTokenClaims) -> str: ...


class TokenVerifier(Protocol):
    def verify(self, token: str) -> AccessTokenClaims: ...
