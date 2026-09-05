from letta_client import AsyncLetta
from letta_client.core.api_error import ApiError

from letta_agent.contracts import LettaGateway
from letta_agent.errors import LettaProviderError
from letta_agent.models import LettaAgentSpec, LettaCreatedAgent, LettaInteractionResult


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
        except ApiError as error:
            raise LettaProviderError("Letta agent creation failed") from error

        return LettaCreatedAgent(agent_id=agent.id)

    async def interact(
        self,
        *,
        agent_id: str,
        message: str,
    ) -> LettaInteractionResult:
        try:
            await self._client.agents.messages.create(
                agent_id=agent_id,
                input=message,
            )
        except ApiError as error:
            raise LettaProviderError("Letta agent interaction failed") from error

        return LettaInteractionResult(succeeded=True)
