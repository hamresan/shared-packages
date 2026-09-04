"""Account/profile application service."""

from instagram_api.application.contracts.accounts import (
    InstagramAccountProvider,
    InstagramAccountReader,
)
from instagram_api.application.contracts.connection import InstagramConnectionReader
from instagram_api.domain import InstagramAccount, InstagramConnectionId

from .policy import InstagramAccountAccessPolicy


class InstagramAccountService(InstagramAccountReader):
    """Reads a selected Instagram account through explicit boundaries."""

    def __init__(
        self,
        connection_reader: InstagramConnectionReader,
        account_provider: InstagramAccountProvider,
        access_policy: InstagramAccountAccessPolicy,
    ) -> None:
        self._connection_reader = connection_reader
        self._account_provider = account_provider
        self._access_policy = access_policy

    async def get_account(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramAccount:
        connection = await self._connection_reader.get_connection(connection_id)
        self._access_policy.validate_connection(connection)

        account = await self._account_provider.get_account(connection_id)
        self._access_policy.validate_account(connection, account)
        return account
