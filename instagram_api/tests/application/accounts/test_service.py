"""Instagram account service tests."""

import asyncio

import pytest

from instagram_api.application.accounts import (
    InstagramAccountAccessPolicy,
    InstagramAccountMismatchError,
    InstagramAccountService,
    InstagramConnectionUnavailableError,
)
from instagram_api.domain import (
    InstagramAccount,
    InstagramAccountId,
    InstagramConnection,
    InstagramConnectionId,
)
from tests.fakes import FakeInstagramAccountProvider, FakeInstagramConnectionReader


def test_service_reads_selected_connection_account() -> None:
    first_id = InstagramConnectionId("connection-a")
    second_id = InstagramConnectionId("connection-b")
    first_account_id = InstagramAccountId("account-a")
    second_account_id = InstagramAccountId("account-b")
    connection_reader = FakeInstagramConnectionReader(
        {
            first_id: InstagramConnection(
                id=first_id,
                provider_account_id=first_account_id,
                permissions=frozenset({"instagram_business_basic"}),
                is_usable=True,
            ),
            second_id: InstagramConnection(
                id=second_id,
                provider_account_id=second_account_id,
                permissions=frozenset({"instagram_business_basic"}),
                is_usable=True,
            ),
        }
    )
    provider = FakeInstagramAccountProvider(
        {
            first_id: InstagramAccount(id=first_account_id, username="account_a"),
            second_id: InstagramAccount(id=second_account_id, username="account_b"),
        }
    )
    service = InstagramAccountService(
        connection_reader,
        provider,
        InstagramAccountAccessPolicy(),
    )

    first = asyncio.run(service.get_account(first_id))
    second = asyncio.run(service.get_account(second_id))

    assert first.username == "account_a"
    assert second.username == "account_b"
    assert provider.requested_connection_ids == [first_id, second_id]


def test_service_does_not_call_provider_for_unusable_connection() -> None:
    connection_id = InstagramConnectionId("connection")
    account_id = InstagramAccountId("account")
    provider = FakeInstagramAccountProvider(
        {connection_id: InstagramAccount(id=account_id, username="shop")}
    )
    service = InstagramAccountService(
        FakeInstagramConnectionReader(
            {
                connection_id: InstagramConnection(
                    id=connection_id,
                    provider_account_id=account_id,
                    permissions=frozenset({"instagram_business_basic"}),
                    is_usable=False,
                )
            }
        ),
        provider,
        InstagramAccountAccessPolicy(),
    )

    with pytest.raises(InstagramConnectionUnavailableError):
        asyncio.run(service.get_account(connection_id))

    assert provider.requested_connection_ids == []


def test_service_rejects_provider_account_mismatch() -> None:
    connection_id = InstagramConnectionId("connection")
    service = InstagramAccountService(
        FakeInstagramConnectionReader(
            {
                connection_id: InstagramConnection(
                    id=connection_id,
                    provider_account_id=InstagramAccountId("expected"),
                    permissions=frozenset({"instagram_business_basic"}),
                    is_usable=True,
                )
            }
        ),
        FakeInstagramAccountProvider(
            {
                connection_id: InstagramAccount(
                    id=InstagramAccountId("unexpected"),
                    username="shop",
                )
            }
        ),
        InstagramAccountAccessPolicy(),
    )

    with pytest.raises(InstagramAccountMismatchError):
        asyncio.run(service.get_account(connection_id))
