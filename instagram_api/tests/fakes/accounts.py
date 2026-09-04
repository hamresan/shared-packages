"""Account reader fake."""

from instagram_api.application.contracts.accounts import InstagramAccountReader
from instagram_api.domain import InstagramAccount, InstagramConnectionId


class FakeInstagramAccountReader(InstagramAccountReader):
    """Fake account reader keyed strictly by connection ID."""

    def __init__(self, accounts: dict[InstagramConnectionId, InstagramAccount]) -> None:
        self._accounts = accounts

    async def get_account(self, connection_id: InstagramConnectionId) -> InstagramAccount:
        return self._accounts[connection_id]
