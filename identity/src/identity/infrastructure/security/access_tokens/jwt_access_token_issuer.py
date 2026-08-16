from datetime import timedelta
from uuid import UUID

from identity.application.contracts.security import Clock, IssuedAccessToken
from identity.infrastructure.security.access_tokens.contracts import AccessTokenClaims, TokenSigner


class JwtAccessTokenIssuer:
    def __init__(self, signer: TokenSigner, clock: Clock, ttl: timedelta) -> None:
        self._signer = signer
        self._clock = clock
        self._ttl = ttl

    async def issue(self, user_id: UUID, session_id: UUID) -> IssuedAccessToken:
        issued_at = self._clock.now()
        expires_at = issued_at + self._ttl
        token = self._signer.sign(
            AccessTokenClaims(
                user_id=user_id,
                session_id=session_id,
                issued_at=issued_at,
                expires_at=expires_at,
            )
        )
        return IssuedAccessToken(token=token, expires_at=expires_at)
