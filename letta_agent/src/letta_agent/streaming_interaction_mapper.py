from collections.abc import AsyncIterable

from letta_client.types.agents.assistant_message import AssistantMessage
from letta_client.types.agents.letta_streaming_response import (
    LettaErrorMessage,
    LettaStopReason,
    LettaStreamingResponse,
)

from letta_agent.errors import LettaProviderError
from letta_agent.models import LettaInteractionResult


class LettaStreamingInteractionResponseMapper:
    """Consume a Letta interaction stream and normalize it to one reply result."""

    async def to_result(
        self,
        response: AsyncIterable[LettaStreamingResponse],
    ) -> LettaInteractionResult:
        reply_text: str | None = None
        stop_reason: str | None = None

        async for event in response:
            print("LETTA_STREAM_EVENT:", type(event).__name__, repr(event))
            if isinstance(event, LettaErrorMessage):
                raise LettaProviderError(f"Letta conversation interaction failed: {event.message}")

            if (
                isinstance(event, AssistantMessage)
                and isinstance(event.content, str)
                and event.content.strip()
            ):
                reply_text = event.content.strip()

            if isinstance(event, LettaStopReason):
                stop_reason = event.stop_reason

        if stop_reason != "end_turn":
            raise LettaProviderError("Letta conversation interaction did not complete successfully")

        return LettaInteractionResult(
            succeeded=True,
            reply_text=reply_text,
        )
