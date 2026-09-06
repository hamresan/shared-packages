from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from letta_agent.errors import LettaProviderError
from letta_agent.models import LettaInteractionResult


@runtime_checkable
class _StopReasonResponse(Protocol):
    stop_reason: str


@runtime_checkable
class _InteractionMessage(Protocol):
    content: object


@runtime_checkable
class _InteractionResponse(Protocol):
    stop_reason: _StopReasonResponse
    messages: Sequence[_InteractionMessage]


class LettaInteractionResponseMapper:
    """Validate and normalize provider interaction responses."""

    def to_result(self, response: object) -> LettaInteractionResult:
        if not isinstance(response, _InteractionResponse):
            raise LettaProviderError("Letta returned an unexpected interaction response")

        if response.stop_reason.stop_reason != "end_turn":
            raise LettaProviderError(
                "Letta agent interaction did not complete successfully"
            )

        reply_text: str | None = None
        for response_message in reversed(response.messages):
            content = response_message.content
            if isinstance(content, str) and content.strip():
                reply_text = content.strip()
                break

        return LettaInteractionResult(
            succeeded=True,
            reply_text=reply_text,
        )
