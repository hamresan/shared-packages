from identity.application.contracts.security import Clock
from identity.application.contracts.session_reader import SessionReader
from identity.application.contracts.user_reader import UserReader
from identity.application.policies.user_status import UserStatusPolicy
from identity.infrastructure.security.access_tokens.contracts import TokenVerifier
from identity.public import AuthenticatedPrincipal


class JwtAccessTokenAuthenticator:
    def __init__(
        self,
        verifier: TokenVerifier,
        session_reader: SessionReader,
        user_reader: UserReader,
        user_status_policy: UserStatusPolicy,
        clock: Clock,
    ) -> None:
        self._verifier = verifier
        self._session_reader = session_reader
        self._user_reader = user_reader
        self._user_status_policy = user_status_policy
        self._clock = clock

    async def authenticate(self, access_token: str) -> AuthenticatedPrincipal:
        claims = self._verifier.verify(access_token)
        session = await self._session_reader.get_by_id(claims.session_id)
        now = self._clock.now()

        if session is None:
            raise ValueError("Session not found")
        if session.user_id != claims.user_id:
            raise ValueError("Session does not belong to token subject")
        if session.revoked_at is not None:
            raise ValueError("Session is revoked")
        if session.expires_at <= now:
            raise ValueError("Session is expired")
        if claims.expires_at <= now:
            raise ValueError("Access token is expired")

        user = await self._user_reader.get_by_id(claims.user_id)
        if user is None:
            raise ValueError("User not found")
        self._user_status_policy.ensure_active(user)

        return AuthenticatedPrincipal(
            user_id=claims.user_id,
            session_id=claims.session_id,
            authentication_method="jwt",
            issued_at=claims.issued_at,
            expires_at=claims.expires_at,
        )
