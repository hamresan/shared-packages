from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from identity.access_tokens import (
    JwtAccessTokenAuthenticator,
    JwtAccessTokenIssuer,
    JwtTokenError,
    PyJwtHmacCodec,
)
from identity.application.policies.user_status import UserStatusPolicy
from identity.domain import UserStatus
from identity.infrastructure.security.access_tokens.contracts import AccessTokenClaims
from identity.public import AccessTokenAuthenticationError
from tests.support.access_tokens import (
    FakeSessionReader,
    FakeTokenCodec,
    FakeUserReader,
    FixedClock,
    build_claims,
    build_session,
    build_user,
    utc_now,
)

TEST_JWT_SECRET = "test-jwt-secret-with-at-least-32-bytes"


def test_pyjwt_codec_round_trip() -> None:
    now = datetime.now(UTC)
    claims = AccessTokenClaims(
        user_id=uuid4(),
        session_id=uuid4(),
        issued_at=now,
        expires_at=now + timedelta(minutes=15),
    )
    codec = PyJwtHmacCodec(TEST_JWT_SECRET)

    token = codec.sign(claims)

    assert codec.verify(token) == claims


def test_pyjwt_codec_rejects_expired_token() -> None:
    now = datetime.now(UTC)
    claims = AccessTokenClaims(
        user_id=uuid4(),
        session_id=uuid4(),
        issued_at=now - timedelta(minutes=30),
        expires_at=now - timedelta(minutes=15),
    )
    codec = PyJwtHmacCodec(TEST_JWT_SECRET)

    token = codec.sign(claims)

    with pytest.raises(JwtTokenError):
        codec.verify(token)


def test_pyjwt_codec_rejects_short_hmac_secret() -> None:
    with pytest.raises(ValueError, match="at least 32 bytes"):
        PyJwtHmacCodec("test-secret")


def test_pyjwt_codec_rejects_invalid_token() -> None:
    codec = PyJwtHmacCodec(TEST_JWT_SECRET)

    with pytest.raises(JwtTokenError):
        codec.verify("not-a-jwt")


@pytest.mark.asyncio
async def test_issuer_uses_signer_and_ttl() -> None:
    now = utc_now()
    user_id = uuid4()
    session_id = uuid4()
    codec = FakeTokenCodec(build_claims(user_id=user_id, session_id=session_id, now=now))
    issuer = JwtAccessTokenIssuer(codec, FixedClock(now), timedelta(minutes=10))

    result = await issuer.issue(user_id, session_id)

    assert result.token == "signed-token"
    assert result.expires_at == now + timedelta(minutes=10)
    assert codec.last_signed_claims is not None
    assert codec.last_signed_claims.user_id == user_id
    assert codec.last_signed_claims.session_id == session_id


@pytest.mark.asyncio
async def test_authenticator_returns_principal_for_active_user_and_session() -> None:
    now = utc_now()
    user_id = uuid4()
    session_id = uuid4()
    claims = build_claims(user_id=user_id, session_id=session_id, now=now)
    session = build_session(user_id=user_id, session_id=session_id, now=now)
    user = build_user(user_id=user_id, now=now)
    authenticator = JwtAccessTokenAuthenticator(
        FakeTokenCodec(claims),
        FakeSessionReader(session),
        FakeUserReader(user),
        UserStatusPolicy(),
        FixedClock(now),
    )

    principal = await authenticator.authenticate("token")

    assert principal.user_id == user_id
    assert principal.session_id == session_id
    assert principal.authentication_method == "jwt"


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["missing", "revoked", "session_expired", "token_expired"])
async def test_authenticator_rejects_invalid_session_or_token(failure: str) -> None:
    now = utc_now()
    user_id = uuid4()
    session_id = uuid4()
    claims = build_claims(
        user_id=user_id,
        session_id=session_id,
        now=now,
        expires_at=now - timedelta(seconds=1) if failure == "token_expired" else None,
    )
    session = None
    if failure != "missing":
        session = build_session(
            user_id=user_id,
            session_id=session_id,
            now=now,
            revoked_at=now if failure == "revoked" else None,
            expires_at=now - timedelta(seconds=1) if failure == "session_expired" else None,
        )
    authenticator = JwtAccessTokenAuthenticator(
        FakeTokenCodec(claims),
        FakeSessionReader(session),
        FakeUserReader(build_user(user_id=user_id, now=now)),
        UserStatusPolicy(),
        FixedClock(now),
    )

    with pytest.raises(AccessTokenAuthenticationError):
        await authenticator.authenticate("token")


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [UserStatus.PENDING, UserStatus.SUSPENDED, UserStatus.DISABLED])
async def test_authenticator_rejects_non_active_user(status: UserStatus) -> None:
    now = utc_now()
    user_id = uuid4()
    session_id = uuid4()
    claims = build_claims(user_id=user_id, session_id=session_id, now=now)
    session = build_session(user_id=user_id, session_id=session_id, now=now)
    user = build_user(user_id=user_id, now=now, status=status)
    authenticator = JwtAccessTokenAuthenticator(
        FakeTokenCodec(claims),
        FakeSessionReader(session),
        FakeUserReader(user),
        UserStatusPolicy(),
        FixedClock(now),
    )

    with pytest.raises(AccessTokenAuthenticationError):
        await authenticator.authenticate("token")
