from letta_agent.contracts import LettaGateway
from letta_agent.models import (
    LettaAgentSpec,
    LettaCreatedAgent,
    LettaInteractionResult,
    LettaKnowledgeResult,
)


class LettaAgentService:
    def __init__(self, gateway: LettaGateway) -> None:
        self._gateway = gateway

    async def create(self, spec: LettaAgentSpec) -> LettaCreatedAgent:
        return await self._gateway.create_agent(spec)

    async def set_knowledge(
        self,
        *,
        agent_id: str,
        value: str,
    ) -> LettaKnowledgeResult:
        return await self._gateway.set_knowledge(
            agent_id=agent_id,
            value=value,
        )

    async def interact(
        self,
        *,
        agent_id: str,
        message: str,
    ) -> LettaInteractionResult:
        return await self._gateway.interact(agent_id=agent_id, message=message)
