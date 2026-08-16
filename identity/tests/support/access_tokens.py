from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from identity.domain import Session
from identity.infrastructure.security.access_tokens.contracts import AccessTokenClaims


class FixedClock:
    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


class FakeSessionReader:
    def __init__(self, session: Session | None) -> None:
        self._session = session

    async def get_by_id(self, session_id: UUID) -> Session | None:
        if self._session is None or self._session.id != session_id:
            return None
        return self._session


class FakeTokenCodec:
    def __init__(self, claims: AccessTokenClaims) -> None:
        self.claims = claims
        self.last_signed_claims: AccessTokenClaims | None = None

    def sign(self, claims: AccessTokenClaims) -> str:
        self.last_signed_claims = claims
        return "signed-token"

    def verify(self, token: str) -> AccessTokenClaims:
        return self.claims


def build_session(
    *,
    user_id: UUID,
    session_id: UUID,
    now: datetime,
    revoked_at: datetime | None = None,
    expires_at: datetime | None = None,
) -> Session:
    return Session(
        id=session_id,
        user_id=user_id,
        refresh_token_hash="refresh-hash",
        family_id=uuid4(),
        parent_session_id=None,
        replaced_by_session_id=None,
        expires_at=expires_at or now + timedelta(days=1),
        revoked_at=revoked_at,
        device_info=None,
        ip_address=None,
        created_at=now,
        last_used_at=None,
    )


def build_claims(
    *,
    user_id: UUID,
    session_id: UUID,
    now: datetime,
    expires_at: datetime | None = None,
) -> AccessTokenClaims:
    return AccessTokenClaims(
        user_id=user_id,
        session_id=session_id,
        issued_at=now,
        expires_at=expires_at or now + timedelta(minutes=15),
    )


def utc_now() -> datetime:
    return datetime(2026, 8, 16, 12, 0, tzinfo=UTC)
