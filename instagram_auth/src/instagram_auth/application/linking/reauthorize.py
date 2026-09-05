"""Refresh one explicitly selected Instagram connection authorization."""

from instagram_auth.application.contracts import InstagramAuthUnitOfWork
from instagram_auth.application.credentials.factory import InstagramProtectedCredentialFactory
from instagram_auth.application.errors.connection_access import (
    InstagramConnectionIdentityMismatchError,
    InstagramConnectionNotFoundError,
)
from instagram_auth.domain import InstagramConnectionId

from .factory import InstagramConnectionFactory
from .models import InstagramConnectionLinkResult, ReauthorizeInstagramConnectionCommand
from ..connections.policy import InstagramConnectionOwnershipPolicy


class ReauthorizeInstagramConnection:
    """Refresh credentials for one owned connection without creating a duplicate."""

    def __init__(
        self,
        *,
        unit_of_work: InstagramAuthUnitOfWork,
        ownership_policy: InstagramConnectionOwnershipPolicy,
        connection_factory: InstagramConnectionFactory,
        credential_factory: InstagramProtectedCredentialFactory,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._ownership_policy = ownership_policy
        self._connection_factory = connection_factory
        self._credential_factory = credential_factory

    async def execute(
        self,
        command: ReauthorizeInstagramConnectionCommand,
    ) -> InstagramConnectionLinkResult:
        async with self._unit_of_work:
            connection = await self._unit_of_work.connections.get_by_id(
                InstagramConnectionId(command.connection_id)
            )
            if connection is None:
                raise InstagramConnectionNotFoundError("Instagram connection not found")

            self._ownership_policy.ensure_owner(
                owner_user_id=command.owner_user_id,
                connection=connection,
            )
            if connection.instagram_account_id != command.identity.provider_user_id:
                raise InstagramConnectionIdentityMismatchError(
                    "Instagram authorization does not match the selected connection"
                )

            refreshed = self._connection_factory.build(
                owner_user_id=command.owner_user_id,
                identity=command.identity,
                grant=command.grant,
                existing=connection,
            )
            await self._unit_of_work.connections.update(refreshed)
            credential = self._credential_factory.build(
                connection_id=refreshed.id,
                grant=command.grant,
            )
            await self._unit_of_work.credentials.save(credential)
            await self._unit_of_work.commit()

        return InstagramConnectionLinkResult(
            connection_id=refreshed.id,
            owner_user_id=command.owner_user_id,
            created=False,
        )
