from letta_agent.contracts import LettaGateway
from letta_agent.models import LettaAgentSpec, LettaCreatedAgent, LettaInteractionResult


class LettaAgentService:
    def __init__(self, gateway: LettaGateway) -> None:
        self._gateway = gateway

    async def create(self, spec: LettaAgentSpec) -> LettaCreatedAgent:
        return await self._gateway.create_agent(spec)

    async def interact(
        self,
        *,
        agent_id: str,
        message: str,
    ) -> LettaInteractionResult:
        return await self._gateway.interact(agent_id=agent_id, message=message)
