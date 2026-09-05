import asyncio
from types import SimpleNamespace

import pytest
from letta_client import AsyncLetta

from letta_agent.models import LettaAgentSpec
from letta_agent.sdk_gateway import SdkLettaGateway


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
    result = asyncio.run(
        gateway.interact(agent_id=created.agent_id, message=message)
    )

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
