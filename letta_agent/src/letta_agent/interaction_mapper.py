from letta_client.types.agents.letta_response import LettaResponse

from letta_agent.errors import LettaProviderError
from letta_agent.models import LettaInteractionResult


class LettaInteractionResponseMapper:
    def to_result(self, response: LettaResponse) -> LettaInteractionResult:
        if response.stop_reason.stop_reason != "end_turn":
            raise LettaProviderError("Letta agent interaction did not complete successfully")

        reply_text: str | None = None
        for response_message in reversed(response.messages):
            content = getattr(response_message, "content", None)
            if isinstance(content, str) and content.strip():
                reply_text = content.strip()
                break

        return LettaInteractionResult(
            succeeded=True,
            reply_text=reply_text,
        )
