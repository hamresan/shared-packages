from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from identity import (
    AccessTokenAuthenticator,
    AccessTokenIssuer,
    AuthenticatedPrincipal,
    IssuedAccessToken,
)


class InMemoryAccessTokenAdapter(AccessTokenIssuer, AccessTokenAuthenticator):
    def __init__(self) -> None:
        self._principals: dict[str, AuthenticatedPrincipal] = {}

    async def issue(self, user_id: UUID, session_id: UUID) -> IssuedAccessToken:
        issued_at = datetime.now(UTC)
        expires_at = issued_at + timedelta(minutes=15)
        token = f"access-{uuid4()}"
        self._principals[token] = AuthenticatedPrincipal(
            user_id=user_id,
            session_id=session_id,
            authentication_method="otp",
            issued_at=issued_at,
            expires_at=expires_at,
        )
        return IssuedAccessToken(token=token, expires_at=expires_at)

    async def authenticate(self, access_token: str) -> AuthenticatedPrincipal:
        principal = self._principals.get(access_token)
        if principal is None:
            raise ValueError("Invalid access token")
        return principal
