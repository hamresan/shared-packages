from typing import Protocol

from letta_agent.models import LettaAgentSpec, LettaCreatedAgent, LettaInteractionResult


class LettaGateway(Protocol):
    async def create_agent(self, spec: LettaAgentSpec) -> LettaCreatedAgent: ...

    async def interact(
        self,
        *,
        agent_id: str,
        message: str,
    ) -> LettaInteractionResult: ...
