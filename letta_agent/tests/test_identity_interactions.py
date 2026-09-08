import asyncio
from types import SimpleNamespace

import pytest
from letta_client import AsyncLetta

from letta_agent.sdk_gateway import SdkLettaGateway


def test_sdk_gateway_sends_sender_identity_for_direct_interaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AsyncLetta(api_key="test-key")
    message_calls: list[dict[str, object]] = []

    async def fake_message_create(**kwargs: object) -> SimpleNamespace:
        message_calls.append(kwargs)
        return SimpleNamespace(
            messages=[
                SimpleNamespace(
                    message_type="assistant_message",
                    content="Welcome back.",
                )
            ],
            stop_reason=SimpleNamespace(stop_reason="end_turn"),
        )

    monkeypatch.setattr(client.agents.messages, "create", fake_message_create)

    result = asyncio.run(
        SdkLettaGateway(client).interact(
            agent_id="agent-1",
            message="Do you remember my size?",
            sender_id="identity-customer-1",
        )
    )

    assert result.reply_text == "Welcome back."
    assert message_calls == [
        {
            "agent_id": "agent-1",
            "messages": [
                {
                    "role": "user",
                    "content": "Do you remember my size?",
                    "sender_id": "identity-customer-1",
                }
            ],
        }
    ]


def test_sdk_gateway_sends_sender_identity_inside_conversation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = AsyncLetta(api_key="test-key")
    message_calls: list[tuple[str, dict[str, object]]] = []

    class FakeRawResponse:
        @staticmethod
        async def json() -> dict[str, object]:
            return {
                "messages": [
                    {
                        "message_type": "assistant_message",
                        "id": "message-1",
                        "date": "2026-09-08T00:00:00Z",
                        "content": "Yes, I remember.",
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

    monkeypatch.setattr(
        client.conversations.messages.with_raw_response,
        "create",
        fake_conversation_message_create,
    )

    result = asyncio.run(
        SdkLettaGateway(client).interact_in_conversation(
            agent_id="agent-1",
            conversation_id="conversation-1",
            message="Do you remember my size?",
            sender_id="identity-customer-1",
        )
    )

    assert result.reply_text == "Yes, I remember."
    assert message_calls == [
        (
            "conversation-1",
            {
                "agent_id": "agent-1",
                "messages": [
                    {
                        "role": "user",
                        "content": "Do you remember my size?",
                        "sender_id": "identity-customer-1",
                    }
                ],
                "streaming": False,
            },
        )
    ]
