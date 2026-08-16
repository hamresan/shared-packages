from datetime import UTC, datetime
from uuid import UUID

import jwt
from jwt import InvalidTokenError

from identity.infrastructure.security.access_tokens.contracts import AccessTokenClaims


class JwtTokenError(ValueError):
    pass


class PyJwtHmacCodec:
    def __init__(self, secret: str, algorithm: str = "HS256") -> None:
        self._secret = secret
        self._algorithm = algorithm

    def sign(self, claims: AccessTokenClaims) -> str:
        payload = {
            "sub": str(claims.user_id),
            "sid": str(claims.session_id),
            "iat": int(claims.issued_at.timestamp()),
            "exp": int(claims.expires_at.timestamp()),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def verify(self, token: str) -> AccessTokenClaims:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            user_id = UUID(str(payload["sub"]))
            session_id = UUID(str(payload["sid"]))
            issued_at = datetime.fromtimestamp(int(payload["iat"]), tz=UTC)
            expires_at = datetime.fromtimestamp(int(payload["exp"]), tz=UTC)
        except (InvalidTokenError, KeyError, TypeError, ValueError) as exc:
            raise JwtTokenError("Invalid access token") from exc

        return AccessTokenClaims(
            user_id=user_id,
            session_id=session_id,
            issued_at=issued_at,
            expires_at=expires_at,
        )
