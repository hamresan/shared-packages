from datetime import UTC, datetime, timedelta
from uuid import uuid4

from identity.public import AccessTokenAuthenticationError, AuthenticatedPrincipal


class FakeAccessTokenAuthenticator:
    async def authenticate(self, access_token: str) -> AuthenticatedPrincipal:
        if access_token != "valid-token":
            raise AccessTokenAuthenticationError("Invalid access token")

        now = datetime.now(UTC)
        return AuthenticatedPrincipal(
            user_id=uuid4(),
            session_id=uuid4(),
            authentication_method="otp",
            issued_at=now,
            expires_at=now + timedelta(minutes=15),
        )


class FailingAccessTokenAuthenticator:
    async def authenticate(self, access_token: str) -> AuthenticatedPrincipal:
        raise RuntimeError("Authentication backend unavailable")
