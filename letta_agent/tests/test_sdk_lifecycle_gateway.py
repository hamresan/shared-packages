import asyncio

import pytest
from letta_client import AsyncLetta

from letta_agent.errors import LettaProviderError
from letta_agent.sdk_lifecycle_gateway import SdkLettaAgentLifecycleGateway
from tests.support.http_errors import build_status_error


def test_sdk_lifecycle_gateway_deletes_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    client = AsyncLetta(api_key="test-key")
    deleted_agent_ids: list[str] = []

    async def fake_delete(agent_id: str) -> None:
        deleted_agent_ids.append(agent_id)

    monkeypatch.setattr(client.agents, "delete", fake_delete)

    asyncio.run(SdkLettaAgentLifecycleGateway(client).delete_agent(agent_id="agent-1"))

    assert deleted_agent_ids == ["agent-1"]


def test_sdk_lifecycle_gateway_treats_missing_agent_as_deleted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AsyncLetta(api_key="test-key")

    async def fake_delete(agent_id: str) -> None:
        del agent_id
        raise build_status_error(404)

    monkeypatch.setattr(client.agents, "delete", fake_delete)

    asyncio.run(SdkLettaAgentLifecycleGateway(client).delete_agent(agent_id="agent-1"))


def test_sdk_lifecycle_gateway_normalizes_deletion_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AsyncLetta(api_key="test-key")

    async def fake_delete(agent_id: str) -> None:
        del agent_id
        raise build_status_error(500)

    monkeypatch.setattr(client.agents, "delete", fake_delete)

    with pytest.raises(LettaProviderError, match="Letta agent deletion failed"):
        asyncio.run(SdkLettaAgentLifecycleGateway(client).delete_agent(agent_id="agent-1"))
