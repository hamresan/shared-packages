from identity import AccessTokenAuthenticator, AuthenticatedPrincipal


class FailingAccessTokenAuthenticator(AccessTokenAuthenticator):
    async def authenticate(self, access_token: str) -> AuthenticatedPrincipal:
        raise RuntimeError("Authentication backend unavailable")
