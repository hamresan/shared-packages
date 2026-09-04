"""Account reader and provider fakes."""

from instagram_api.application.contracts.accounts import (
    InstagramAccountProvider,
    InstagramAccountReader,
)
from instagram_api.domain import InstagramAccount, InstagramConnectionId


class FakeInstagramAccountReader(InstagramAccountReader):
    """Fake account reader keyed strictly by connection ID."""

    def __init__(self, accounts: dict[InstagramConnectionId, InstagramAccount]) -> None:
        self._accounts = accounts

    async def get_account(self, connection_id: InstagramConnectionId) -> InstagramAccount:
        return self._accounts[connection_id]


class FakeInstagramAccountProvider(InstagramAccountProvider):
    """Fake provider keyed strictly by connection ID."""

    def __init__(self, accounts: dict[InstagramConnectionId, InstagramAccount]) -> None:
        self._accounts = accounts
        self.requested_connection_ids: list[InstagramConnectionId] = []

    async def get_account(self, connection_id: InstagramConnectionId) -> InstagramAccount:
        self.requested_connection_ids.append(connection_id)
        return self._accounts[connection_id]
