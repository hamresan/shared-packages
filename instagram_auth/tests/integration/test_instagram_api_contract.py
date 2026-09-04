"""Verify real public-contract integration with hamresan-instagram-api."""

import asyncio
from datetime import UTC, datetime
from uuid import UUID

from instagram_api.domain import InstagramConnectionId as ApiInstagramConnectionId

from instagram_auth import (
    CORE_PERMISSIONS,
    InstagramAccountType,
    InstagramConnection,
    InstagramConnectionId,
    InstagramConnectionState,
)
from tests.integration.support import (
    InMemoryAuthAccessTokenProvider,
    InMemoryAuthConnectionReader,
    InstagramApiAccessTokenAdapter,
    InstagramApiConnectionReaderAdapter,
)

OWNER_ID = "owner-1"
CONNECTION_A = InstagramConnectionId(UUID("00000000-0000-0000-0000-000000000101"))
CONNECTION_B = InstagramConnectionId(UUID("00000000-0000-0000-0000-000000000102"))


def build_connection(
    connection_id: InstagramConnectionId,
    provider_account_id: str,
) -> InstagramConnection:
    """Build one auth-owned connection for the shared owner."""

    return InstagramConnection(
        id=connection_id,
        owner_user_id=OWNER_ID,
        instagram_account_id=provider_account_id,
        username=provider_account_id,
        account_type=InstagramAccountType.BUSINESS,
        permissions=CORE_PERMISSIONS,
        status=InstagramConnectionState.CONNECTED,
        connected_at=datetime(2026, 9, 4, 12, 0, tzinfo=UTC),
    )


def test_two_auth_connections_adapt_to_api_contracts_without_persistence_coupling() -> None:
    async def scenario() -> None:
        connection_a = build_connection(CONNECTION_A, "provider-a")
        connection_b = build_connection(CONNECTION_B, "provider-b")
        reader = InstagramApiConnectionReaderAdapter(
            InMemoryAuthConnectionReader(
                {
                    CONNECTION_A: connection_a,
                    CONNECTION_B: connection_b,
                }
            )
        )
        tokens = InstagramApiAccessTokenAdapter(
            InMemoryAuthAccessTokenProvider(
                {
                    CONNECTION_A: "token-a",
                    CONNECTION_B: "token-b",
                }
            )
        )

        api_connection_a = ApiInstagramConnectionId(str(CONNECTION_A.value))
        api_connection_b = ApiInstagramConnectionId(str(CONNECTION_B.value))

        resolved_a = await reader.get_connection(api_connection_a)
        resolved_b = await reader.get_connection(api_connection_b)

        assert connection_a.owner_user_id == connection_b.owner_user_id == OWNER_ID
        assert resolved_a.provider_account_id == "provider-a"
        assert resolved_b.provider_account_id == "provider-b"
        assert resolved_a.id != resolved_b.id
        assert await tokens.get_access_token(api_connection_a) == "token-a"
        assert await tokens.get_access_token(api_connection_b) == "token-b"

    asyncio.run(scenario())
