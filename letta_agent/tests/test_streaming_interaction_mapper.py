import asyncio
from datetime import UTC, datetime

import pytest
from letta_client.types.agents.assistant_message import AssistantMessage
from letta_client.types.agents.letta_streaming_response import (
    LettaErrorMessage,
    LettaStopReason,
)

from letta_agent.errors import LettaProviderError
from letta_agent.streaming_interaction_mapper import (
    LettaStreamingInteractionResponseMapper,
)
from tests.support import FakeInteractionStream


def test_stream_mapper_returns_latest_assistant_text() -> None:
    mapper = LettaStreamingInteractionResponseMapper()

    result = asyncio.run(
        mapper.to_result(
            FakeInteractionStream(
                [
                    AssistantMessage(
                        id="message-1",
                        content=" first ",
                        date=datetime.now(UTC),
                    ),
                    AssistantMessage(
                        id="message-2",
                        content=" final reply ",
                        date=datetime.now(UTC),
                    ),
                    LettaStopReason(stop_reason="end_turn"),
                ]
            )
        )
    )

    assert result.succeeded is True
    assert result.reply_text == "final reply"


def test_stream_mapper_normalizes_provider_error_event() -> None:
    mapper = LettaStreamingInteractionResponseMapper()

    with pytest.raises(
        LettaProviderError,
        match="Letta conversation interaction failed",
    ):
        asyncio.run(
            mapper.to_result(
                FakeInteractionStream(
                    [
                        LettaErrorMessage(
                            error_type="provider_error",
                            message="provider failed",
                            message_type="error_message",
                            run_id="run-1",
                        )
                    ]
                )
            )
        )


def test_stream_mapper_requires_successful_stop_reason() -> None:
    mapper = LettaStreamingInteractionResponseMapper()

    with pytest.raises(
        LettaProviderError,
        match="did not complete successfully",
    ):
        asyncio.run(
            mapper.to_result(
                FakeInteractionStream(
                    [
                        AssistantMessage(
                            id="message-1",
                            content="partial",
                            date=datetime.now(UTC),
                        )
                    ]
                )
            )
        )
