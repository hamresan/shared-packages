from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Protocol, cast
from uuid import UUID

import jwt
from jwt import InvalidTokenError

from identity.infrastructure.security.access_tokens.contracts import AccessTokenClaims

JwtPayloadValue = str | int
JwtDecodeOptions = Mapping[str, bool]


class JwtLibrary(Protocol):
    def encode(
        self,
        payload: Mapping[str, JwtPayloadValue],
        key: str,
        algorithm: str,
    ) -> str: ...

    def decode(
        self,
        token: str,
        key: str,
        algorithms: Sequence[str],
        options: JwtDecodeOptions,
    ) -> dict[str, object]: ...


class JwtTokenError(ValueError):
    pass


class PyJwtHmacCodec:
    def __init__(self, secret: str, algorithm: str = "HS256") -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._jwt = cast(JwtLibrary, jwt)

    def sign(self, claims: AccessTokenClaims) -> str:
        payload: dict[str, JwtPayloadValue] = {
            "sub": str(claims.user_id),
            "sid": str(claims.session_id),
            "iat": int(claims.issued_at.timestamp()),
            "exp": int(claims.expires_at.timestamp()),
        }
        return self._jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def verify(self, token: str) -> AccessTokenClaims:
        try:
            payload = self._jwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
                options={"verify_exp": False},
            )
            user_id = UUID(str(payload["sub"]))
            session_id = UUID(str(payload["sid"]))
            issued_at = datetime.fromtimestamp(int(str(payload["iat"])), tz=UTC)
            expires_at = datetime.fromtimestamp(int(str(payload["exp"])), tz=UTC)
        except (InvalidTokenError, KeyError, TypeError, ValueError) as exc:
            raise JwtTokenError("Invalid access token") from exc

        return AccessTokenClaims(
            user_id=user_id,
            session_id=session_id,
            issued_at=issued_at,
            expires_at=expires_at,
        )
