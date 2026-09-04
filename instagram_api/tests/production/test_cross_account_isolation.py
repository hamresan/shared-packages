"""Production regression tests for cross-account isolation."""

import asyncio

import pytest

from instagram_api.application.accounts import (
    InstagramAccountAccessPolicy,
    InstagramAccountMismatchError,
    InstagramAccountService,
)
from instagram_api.application.contracts import (
    InstagramAccountProvider,
    InstagramConnectionReader,
)
from instagram_api.domain import (
    InstagramAccount,
    InstagramAccountId,
    InstagramConnection,
    InstagramConnectionId,
)

BASIC_PERMISSION = "instagram_business_basic"
CONNECTION_A = InstagramConnectionId("connection-a")
CONNECTION_B = InstagramConnectionId("connection-b")


class IsolationConnectionReader(InstagramConnectionReader):
    """Returns only the explicitly requested connection."""

    def __init__(self) -> None:
        self.connections = {
            CONNECTION_A: InstagramConnection(
                id=CONNECTION_A,
                provider_account_id=InstagramAccountId("account-a"),
                permissions=frozenset({BASIC_PERMISSION}),
                is_usable=True,
            ),
            CONNECTION_B: InstagramConnection(
                id=CONNECTION_B,
                provider_account_id=InstagramAccountId("account-b"),
                permissions=frozenset({BASIC_PERMISSION}),
                is_usable=True,
            ),
        }

    async def get_connection(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramConnection:
        return self.connections[connection_id]


class RecordingAccountProvider(InstagramAccountProvider):
    """Records connection selection and can simulate provider-account mismatch."""

    def __init__(self) -> None:
        self.calls: list[InstagramConnectionId] = []
        self.return_wrong_account = False

    async def get_account(
        self,
        connection_id: InstagramConnectionId,
    ) -> InstagramAccount:
        self.calls.append(connection_id)
        account_id = "account-b" if self.return_wrong_account else "account-a"
        return InstagramAccount(
            id=InstagramAccountId(account_id),
            username=account_id,
        )


def test_selected_connection_never_falls_back_to_another_account() -> None:
    async def scenario() -> None:
        provider = RecordingAccountProvider()
        service = InstagramAccountService(
            IsolationConnectionReader(),
            provider,
            InstagramAccountAccessPolicy(),
        )

        account = await service.get_account(CONNECTION_A)

        assert account.id == InstagramAccountId("account-a")
        assert provider.calls == [CONNECTION_A]

    asyncio.run(scenario())


def test_provider_account_mismatch_fails_closed_instead_of_crossing_accounts() -> None:
    async def scenario() -> None:
        provider = RecordingAccountProvider()
        provider.return_wrong_account = True
        service = InstagramAccountService(
            IsolationConnectionReader(),
            provider,
            InstagramAccountAccessPolicy(),
        )

        with pytest.raises(InstagramAccountMismatchError):
            await service.get_account(CONNECTION_A)

        assert provider.calls == [CONNECTION_A]

    asyncio.run(scenario())
