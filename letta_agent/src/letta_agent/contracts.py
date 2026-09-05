from typing import Protocol

from letta_agent.models import (
    LettaAgentSpec,
    LettaCreatedAgent,
    LettaInteractionResult,
    LettaKnowledgeResult,
)


class LettaGateway(Protocol):
    async def create_agent(self, spec: LettaAgentSpec) -> LettaCreatedAgent: ...

    async def set_knowledge(
        self,
        *,
        agent_id: str,
        value: str,
    ) -> LettaKnowledgeResult: ...

    async def interact(
        self,
        *,
        agent_id: str,
        message: str,
    ) -> LettaInteractionResult: ...
