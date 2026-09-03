"""Fakes for downstream Instagram access-boundary tests."""

from instagram_auth.application.contracts import (
    InstagramAccessTokenProtector,
    InstagramConnectionReader,
    InstagramCredentialRepository,
)
from instagram_auth.application.models import InstagramProtectedCredential
from instagram_auth.domain import InstagramConnection, InstagramConnectionId


class FakeInstagramConnectionReader(InstagramConnectionReader):
    def __init__(self, connections: tuple[InstagramConnection, ...] = ()) -> None:
        self.connections = {connection.id: connection for connection in connections}

    async def get(self, connection_id: InstagramConnectionId) -> InstagramConnection | None:
        return self.connections.get(connection_id)


class FakeInstagramCredentialRepository(InstagramCredentialRepository):
    def __init__(self, credentials: tuple[InstagramProtectedCredential, ...] = ()) -> None:
        self.credentials = {credential.connection_id: credential for credential in credentials}

    async def save(self, credential: InstagramProtectedCredential) -> None:
        self.credentials[credential.connection_id] = credential

    async def get(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramProtectedCredential | None:
        return self.credentials.get(connection_id)


class FakeInstagramAccessTokenProtector(InstagramAccessTokenProtector):
    def protect(self, access_token: str) -> str:
        return f"protected:{access_token}"

    def unprotect(self, protected_access_token: str) -> str:
        prefix = "protected:"
        if not protected_access_token.startswith(prefix):
            raise ValueError("Credential is not protected")
        return protected_access_token[len(prefix) :]
