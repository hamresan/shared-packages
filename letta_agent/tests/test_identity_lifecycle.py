import asyncio
from types import SimpleNamespace

import pytest
from letta_client import AsyncLetta

from letta_agent.errors import LettaProviderError
from letta_agent.identity_response import LettaIdentityResponse
from letta_agent.models import LettaIdentity, LettaIdentitySpec
from letta_agent.sdk_gateway import SdkLettaGateway
from tests.support.http_errors import build_status_error


def test_sdk_gateway_upserts_identity_with_custom_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AsyncLetta(api_key="test-key")
    put_calls: list[tuple[str, type[object], dict[str, object]]] = []

    async def fake_put(
        path: str,
        *,
        cast_to: type[object],
        body: dict[str, object],
    ) -> LettaIdentityResponse:
        put_calls.append((path, cast_to, body))
        return LettaIdentityResponse(
            id="identity-1",
            identifier_key="business-1:customer-1",
            name="Instagram customer",
        )

    monkeypatch.setattr(client, "put", fake_put)

    result = asyncio.run(
        SdkLettaGateway(client).upsert_identity(
            LettaIdentitySpec(
                identifier_key="business-1:customer-1",
                name="Instagram customer",
            )
        )
    )

    assert result == LettaIdentity(
        identity_id="identity-1",
        identifier_key="business-1:customer-1",
        name="Instagram customer",
    )
    assert put_calls == [
        (
            "/v1/identities/",
            LettaIdentityResponse,
            {
                "identifier_key": "business-1:customer-1",
                "identity_type": "user",
                "name": "Instagram customer",
            },
        )
    ]


def test_sdk_gateway_attaches_identity_to_agent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AsyncLetta(api_key="test-key")
    attach_calls: list[tuple[str, str]] = []

    async def fake_attach(identity_id: str, *, agent_id: str) -> object:
        attach_calls.append((identity_id, agent_id))
        return SimpleNamespace()

    monkeypatch.setattr(client.agents.identities, "attach", fake_attach)

    asyncio.run(
        SdkLettaGateway(client).attach_identity(
            agent_id="agent-1",
            identity_id="identity-1",
        )
    )

    assert attach_calls == [("identity-1", "agent-1")]


def test_sdk_gateway_normalizes_identity_upsert_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AsyncLetta(api_key="test-key")

    async def fake_put(
        path: str,
        *,
        cast_to: type[object],
        body: dict[str, object],
    ) -> object:
        del path, cast_to, body
        raise build_status_error(500)

    monkeypatch.setattr(client, "put", fake_put)

    with pytest.raises(LettaProviderError, match="Letta identity upsert failed"):
        asyncio.run(
            SdkLettaGateway(client).upsert_identity(
                LettaIdentitySpec(
                    identifier_key="business-1:customer-1",
                    name="Instagram customer",
                )
            )
        )


def test_sdk_gateway_normalizes_identity_attachment_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AsyncLetta(api_key="test-key")

    async def fake_attach(identity_id: str, *, agent_id: str) -> object:
        del identity_id, agent_id
        raise build_status_error(500)

    monkeypatch.setattr(client.agents.identities, "attach", fake_attach)

    with pytest.raises(LettaProviderError, match="Letta identity attachment failed"):
        asyncio.run(
            SdkLettaGateway(client).attach_identity(
                agent_id="agent-1",
                identity_id="identity-1",
            )
        )
