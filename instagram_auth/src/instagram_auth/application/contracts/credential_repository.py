"""Protected Instagram credential persistence contract."""

from typing import Protocol

from instagram_auth.application.models import InstagramProtectedCredential
from instagram_auth.domain import InstagramConnectionId


class InstagramCredentialRepository(Protocol):
    """Persistence boundary for protected credentials scoped to one connection."""

    async def save(self, credential: InstagramProtectedCredential) -> None:
        """Persist protected credential material and lifecycle metadata."""
        ...

    async def get(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramProtectedCredential | None:
        """Return the protected credential for one explicit connection."""
        ...
