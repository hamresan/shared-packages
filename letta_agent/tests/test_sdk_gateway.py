import asyncio
from types import SimpleNamespace

import httpx
import pytest
from letta_client import APIStatusError, AsyncLetta

from letta_agent.models import LettaAgentSpec
from letta_agent.sdk_gateway import SdkLettaGateway


def build_not_found() -> APIStatusError:
    request = httpx.Request("GET", "http://localhost/v1/test")
    response = httpx.Response(404, request=request)
    return APIStatusError("Not found", response=response, body=None)


@pytest.mark.parametrize("message", ["Ready?", "Confirm readiness."])
def test_sdk_gateway_maps_create_and_interaction(
    monkeypatch: pytest.MonkeyPatch,
    message: str,
) -> None:
    client = AsyncLetta(api_key="test-key")
    create_calls: list[dict[str, object]] = []
    message_calls: list[dict[str, object]] = []

    async def fake_create(**kwargs: object) -> SimpleNamespace:
        create_calls.append(kwargs)
        return SimpleNamespace(id="agent-1")

    async def fake_message_create(**kwargs: object) -> SimpleNamespace:
        message_calls.append(kwargs)
        return SimpleNamespace(
            messages=[],
            stop_reason=SimpleNamespace(stop_reason="end_turn"),
        )

    monkeypatch.setattr(client.agents, "create", fake_create)
    monkeypatch.setattr(client.agents.messages, "create", fake_message_create)
    gateway = SdkLettaGateway(client)
    spec = LettaAgentSpec(
        name="sellora-agent",
        model="openai/gpt-4.1",
        persona="Keep responses concise.",
    )

    created = asyncio.run(gateway.create_agent(spec))
    result = asyncio.run(gateway.interact(agent_id=created.agent_id, message=message))

    assert created.agent_id == "agent-1"
    assert result.succeeded is True
    assert create_calls == [
        {
            "name": "sellora-agent",
            "model": "openai/gpt-4.1",
            "memory_blocks": [
                {
                    "label": "persona",
                    "value": "Keep responses concise.",
                }
            ],
        }
    ]
    assert message_calls == [
        {
            "agent_id": "agent-1",
            "input": message,
        }
    ]


def test_sdk_gateway_creates_and_attaches_missing_knowledge_block(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AsyncLetta(api_key="test-key")
    create_calls: list[dict[str, object]] = []
    attach_calls: list[tuple[str, str]] = []

    async def fake_retrieve(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise build_not_found()

    async def fake_block_create(**kwargs: object) -> SimpleNamespace:
        create_calls.append(kwargs)
        return SimpleNamespace(id="block-1")

    async def fake_attach(block_id: str, *, agent_id: str) -> object:
        attach_calls.append((block_id, agent_id))
        return SimpleNamespace(id=agent_id)

    monkeypatch.setattr(client.agents.blocks, "retrieve", fake_retrieve)
    monkeypatch.setattr(client.blocks, "create", fake_block_create)
    monkeypatch.setattr(client.agents.blocks, "attach", fake_attach)

    result = asyncio.run(
        SdkLettaGateway(client).set_knowledge(
            agent_id="agent-1",
            value="Authoritative account knowledge",
        )
    )

    assert result.block_id == "block-1"
    assert create_calls == [
        {
            "label": "account_knowledge",
            "value": "Authoritative account knowledge",
            "read_only": True,
        }
    ]
    assert attach_calls == [("block-1", "agent-1")]


def test_sdk_gateway_updates_existing_knowledge_block(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AsyncLetta(api_key="test-key")
    update_calls: list[tuple[str, str, str, bool]] = []

    async def fake_retrieve(
        block_label: str,
        *,
        agent_id: str,
    ) -> SimpleNamespace:
        return SimpleNamespace(id="block-1", label=block_label, agent_id=agent_id)

    async def fake_update(
        block_label: str,
        *,
        agent_id: str,
        value: str,
        read_only: bool,
    ) -> SimpleNamespace:
        update_calls.append((block_label, agent_id, value, read_only))
        return SimpleNamespace(id="block-1")

    monkeypatch.setattr(client.agents.blocks, "retrieve", fake_retrieve)
    monkeypatch.setattr(client.agents.blocks, "update", fake_update)

    result = asyncio.run(
        SdkLettaGateway(client).set_knowledge(
            agent_id="agent-1",
            value="Updated knowledge",
        )
    )

    assert result.block_id == "block-1"
    assert update_calls == [("account_knowledge", "agent-1", "Updated knowledge", True)]
