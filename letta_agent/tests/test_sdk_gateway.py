import asyncio
from types import SimpleNamespace

import httpx
import pytest
from letta_client import APIStatusError, AsyncLetta

from letta_agent.errors import LettaProviderError
from letta_agent.models import LettaAgentSpec
from letta_agent.sdk_gateway import SdkLettaGateway


def build_status_error(status_code: int) -> APIStatusError:
    request = httpx.Request("GET", "http://localhost/v1/test")
    response = httpx.Response(status_code, request=request)
    return APIStatusError(
        f"HTTP {status_code}",
        response=response,
        body=None,
    )


def build_not_found() -> APIStatusError:
    return build_status_error(404)


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
            messages=[
                SimpleNamespace(content="Here is the account reply."),
            ],
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
    assert result.reply_text == "Here is the account reply."
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


def test_sdk_gateway_normalizes_non_404_knowledge_lookup_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AsyncLetta(api_key="test-key")

    async def fake_retrieve(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise build_status_error(500)

    monkeypatch.setattr(client.agents.blocks, "retrieve", fake_retrieve)

    with pytest.raises(
        LettaProviderError,
        match="Letta knowledge lookup failed",
    ):
        asyncio.run(
            SdkLettaGateway(client).set_knowledge(
                agent_id="agent-1",
                value="Knowledge",
            )
        )


def test_sdk_gateway_normalizes_existing_knowledge_update_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AsyncLetta(api_key="test-key")

    async def fake_retrieve(
        block_label: str,
        *,
        agent_id: str,
    ) -> SimpleNamespace:
        return SimpleNamespace(id="block-1", label=block_label, agent_id=agent_id)

    async def fake_update(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise build_status_error(500)

    monkeypatch.setattr(client.agents.blocks, "retrieve", fake_retrieve)
    monkeypatch.setattr(client.agents.blocks, "update", fake_update)

    with pytest.raises(
        LettaProviderError,
        match="Letta knowledge update failed",
    ):
        asyncio.run(
            SdkLettaGateway(client).set_knowledge(
                agent_id="agent-1",
                value="Updated knowledge",
            )
        )


def test_sdk_gateway_normalizes_missing_knowledge_creation_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AsyncLetta(api_key="test-key")

    async def fake_retrieve(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise build_not_found()

    async def fake_block_create(**kwargs: object) -> object:
        del kwargs
        raise build_status_error(500)

    monkeypatch.setattr(client.agents.blocks, "retrieve", fake_retrieve)
    monkeypatch.setattr(client.blocks, "create", fake_block_create)

    with pytest.raises(
        LettaProviderError,
        match="Letta knowledge creation failed",
    ):
        asyncio.run(
            SdkLettaGateway(client).set_knowledge(
                agent_id="agent-1",
                value="Knowledge",
            )
        )


def test_sdk_gateway_configures_agent_tools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AsyncLetta(api_key="test-key")
    update_calls: list[tuple[str, list[str]]] = []

    async def fake_update(
        agent_id: str,
        *,
        tool_ids: list[str],
    ) -> SimpleNamespace:
        update_calls.append((agent_id, tool_ids))
        return SimpleNamespace(id=agent_id)

    monkeypatch.setattr(client.agents, "update", fake_update)

    asyncio.run(
        SdkLettaGateway(client).set_agent_tools(
            agent_id="agent-1",
            tool_ids=(),
        )
    )

    assert update_calls == [("agent-1", [])]


def test_sdk_gateway_creates_and_interacts_in_conversation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AsyncLetta(api_key="test-key")
    conversation_calls: list[dict[str, object]] = []
    message_calls: list[tuple[str, dict[str, object]]] = []

    async def fake_conversation_create(**kwargs: object) -> SimpleNamespace:
        conversation_calls.append(kwargs)
        return SimpleNamespace(id="conversation-1")

    class FakeRawResponse:
        @staticmethod
        async def json() -> dict[str, object]:
            return {
                "messages": [
                    {
                        "message_type": "assistant_message",
                        "id": "message-1",
                        "date": "2026-09-06T00:00:00Z",
                        "content": "I remember the previous turn.",
                    }
                ],
                "stop_reason": {"stop_reason": "end_turn"},
                "usage": {},
            }

    async def fake_conversation_message_create(
        conversation_id: str,
        **kwargs: object,
    ) -> FakeRawResponse:
        message_calls.append((conversation_id, kwargs))
        return FakeRawResponse()

    monkeypatch.setattr(client.conversations, "create", fake_conversation_create)
    monkeypatch.setattr(
        client.conversations.messages.with_raw_response,
        "create",
        fake_conversation_message_create,
    )
    gateway = SdkLettaGateway(client)

    conversation = asyncio.run(gateway.create_conversation(agent_id="agent-1"))
    result = asyncio.run(
        gateway.interact_in_conversation(
            agent_id="agent-1",
            conversation_id=conversation.conversation_id,
            message="What did I ask before?",
        )
    )

    assert conversation.conversation_id == "conversation-1"
    assert result.succeeded is True
    assert result.reply_text == "I remember the previous turn."
    assert conversation_calls == [{"agent_id": "agent-1"}]
    assert message_calls == [
        (
            "conversation-1",
            {
                "agent_id": "agent-1",
                "input": "What did I ask before?",
                "streaming": False,
            },
        )
    ]


def test_sdk_gateway_normalizes_conversation_creation_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AsyncLetta(api_key="test-key")

    async def fake_create(**kwargs: object) -> object:
        del kwargs
        raise build_status_error(500)

    monkeypatch.setattr(client.conversations, "create", fake_create)

    with pytest.raises(
        LettaProviderError,
        match="Letta conversation creation failed",
    ):
        asyncio.run(SdkLettaGateway(client).create_conversation(agent_id="agent-1"))


def test_sdk_gateway_normalizes_conversation_interaction_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AsyncLetta(api_key="test-key")

    async def fake_create(
        conversation_id: str,
        **kwargs: object,
    ) -> object:
        del conversation_id, kwargs
        raise build_status_error(500)

    monkeypatch.setattr(
        client.conversations.messages,
        "create",
        fake_create,
    )

    with pytest.raises(
        LettaProviderError,
        match="Letta conversation interaction failed",
    ):
        asyncio.run(
            SdkLettaGateway(client).interact_in_conversation(
                agent_id="agent-1",
                conversation_id="conversation-1",
                message="Hello",
            )
        )
