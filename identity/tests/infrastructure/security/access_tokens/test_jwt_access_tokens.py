from datetime import timedelta
from uuid import uuid4

import pytest

from identity.access_tokens import (
    JwtAccessTokenAuthenticator,
    JwtAccessTokenIssuer,
    JwtTokenError,
    PyJwtHmacCodec,
)
from identity.infrastructure.security.access_tokens.contracts import AccessTokenClaims
from tests.support.access_tokens import (
    FakeSessionReader,
    FakeTokenCodec,
    FixedClock,
    build_claims,
    build_session,
    utc_now,
)


def test_pyjwt_codec_round_trip() -> None:
    now = utc_now()
    claims = AccessTokenClaims(
        user_id=uuid4(),
        session_id=uuid4(),
        issued_at=now,
        expires_at=now + timedelta(minutes=15),
    )
    codec = PyJwtHmacCodec("test-secret")

    token = codec.sign(claims)

    assert codec.verify(token) == claims


def test_pyjwt_codec_rejects_invalid_token() -> None:
    codec = PyJwtHmacCodec("test-secret")

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
async def test_authenticator_returns_principal_for_active_session() -> None:
    now = utc_now()
    user_id = uuid4()
    session_id = uuid4()
    claims = build_claims(user_id=user_id, session_id=session_id, now=now)
    session = build_session(user_id=user_id, session_id=session_id, now=now)
    authenticator = JwtAccessTokenAuthenticator(
        FakeTokenCodec(claims),
        FakeSessionReader(session),
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
        FixedClock(now),
    )

    with pytest.raises(ValueError):
        await authenticator.authenticate("token")
