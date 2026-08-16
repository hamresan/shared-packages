from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from identity.domain import IdentityType


@dataclass(frozen=True, slots=True)
class IssuedAccessToken:
    token: str
    expires_at: datetime


class Clock(Protocol):
    def now(self) -> datetime: ...


class OtpCodeGenerator(Protocol):
    def generate(self) -> str: ...


class SecretHasher(Protocol):
    def hash(self, value: str) -> str: ...

    def verify(self, value: str, hashed_value: str) -> bool: ...


class RefreshTokenGenerator(Protocol):
    def generate(self) -> str: ...


class AccessTokenIssuer(Protocol):
    async def issue(self, user_id: UUID, session_id: UUID) -> IssuedAccessToken: ...


class IdentityNormalizer(Protocol):
    def normalize(self, identity_type: IdentityType, value: str) -> str: ...
