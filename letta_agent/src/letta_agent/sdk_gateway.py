from letta_client import APIError, AsyncLetta

from letta_agent.contracts import LettaGateway
from letta_agent.errors import LettaProviderError
from letta_agent.models import (
    LettaAgentSpec,
    LettaCreatedAgent,
    LettaInteractionResult,
)


class SdkLettaGateway(LettaGateway):
    def __init__(self, client: AsyncLetta) -> None:
        self._client = client

    async def create_agent(self, spec: LettaAgentSpec) -> LettaCreatedAgent:
        try:
            agent = await self._client.agents.create(
                name=spec.name,
                model=spec.model,
                memory_blocks=[
                    {
                        "label": "persona",
                        "value": spec.persona,
                    }
                ],
            )
        except APIError as error:
            raise LettaProviderError("Letta agent creation failed") from error

        return LettaCreatedAgent(agent_id=agent.id)

    async def interact(
        self,
        *,
        agent_id: str,
        message: str,
    ) -> LettaInteractionResult:
        try:
            response = await self._client.agents.messages.create(
                agent_id=agent_id,
                input=message,
            )
        except APIError as error:
            raise LettaProviderError("Letta agent interaction failed") from error

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
