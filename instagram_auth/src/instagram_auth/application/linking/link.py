"""Persist an Instagram authorization under an explicit host owner."""

from instagram_auth.application.contracts import InstagramAuthUnitOfWork
from instagram_auth.application.credentials.factory import InstagramProtectedCredentialFactory

from .factory import InstagramConnectionFactory
from .models import InstagramConnectionLinkResult, LinkInstagramAuthorizationCommand


class LinkInstagramAuthorization:
    """Create or refresh one Instagram connection after the host resolves ownership."""

    def __init__(
        self,
        unit_of_work: InstagramAuthUnitOfWork,
        connection_factory: InstagramConnectionFactory,
        credential_factory: InstagramProtectedCredentialFactory,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._connection_factory = connection_factory
        self._credential_factory = credential_factory

    async def execute(
        self,
        command: LinkInstagramAuthorizationCommand,
    ) -> InstagramConnectionLinkResult:
        async with self._unit_of_work:
            existing = await self._unit_of_work.connections.find_by_owner_and_account(
                owner_user_id=command.owner_user_id,
                instagram_account_id=command.identity.provider_user_id,
            )
            connection = self._connection_factory.build(
                owner_user_id=command.owner_user_id,
                identity=command.identity,
                grant=command.grant,
                existing=existing,
            )
            if existing is None:
                await self._unit_of_work.connections.add(connection)
            else:
                await self._unit_of_work.connections.update(connection)
            credential = self._credential_factory.build(
                connection_id=connection.id,
                grant=command.grant,
            )
            await self._unit_of_work.credentials.save(credential)
            await self._unit_of_work.commit()
        return InstagramConnectionLinkResult(
            connection_id=connection.id,
            owner_user_id=command.owner_user_id,
            created=existing is None,
        )
