"""Authorized access-token provider for downstream Instagram API operations."""

from collections.abc import Collection

from instagram_auth.application.contracts import (
    InstagramAccessTokenProtector,
    InstagramConnectionReader,
    InstagramCredentialRepository,
)
from instagram_auth.application.errors.access import InstagramConnectionUnavailableError
from instagram_auth.baseline import InstagramPermission
from instagram_auth.domain import InstagramConnectionId

from .policy import InstagramConnectionAccessPolicy


class AuthorizedInstagramAccessTokenProvider:
    """Resolve one selected connection and expose its token only when usable."""

    def __init__(
        self,
        connection_reader: InstagramConnectionReader,
        credential_repository: InstagramCredentialRepository,
        token_protector: InstagramAccessTokenProtector,
        access_policy: InstagramConnectionAccessPolicy,
    ) -> None:
        self._connection_reader = connection_reader
        self._credential_repository = credential_repository
        self._token_protector = token_protector
        self._access_policy = access_policy

    async def get_access_token(
        self,
        *,
        connection_id: InstagramConnectionId,
        required_permissions: Collection[InstagramPermission] = (),
    ) -> str:
        connection = await self._connection_reader.get(connection_id)
        if connection is None:
            raise InstagramConnectionUnavailableError("Instagram connection not found")
        self._access_policy.validate(
            connection=connection,
            required_permissions=required_permissions,
        )
        credential = await self._credential_repository.get(connection_id)
        if credential is None or credential.revoked_at is not None:
            raise InstagramConnectionUnavailableError("Instagram credential is unavailable")
        return self._token_protector.unprotect(credential.protected_access_token)
