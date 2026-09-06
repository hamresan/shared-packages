from collections.abc import Sequence
from typing import Protocol

from letta_agent.models import (
    LettaAgentSpec,
    LettaCreatedAgent,
    LettaCreatedConversation,
    LettaInteractionResult,
    LettaKnowledgeResult,
)


class LettaGateway(Protocol):
    async def create_agent(self, spec: LettaAgentSpec) -> LettaCreatedAgent: ...

    async def create_conversation(
        self,
        *,
        agent_id: str,
    ) -> LettaCreatedConversation: ...

    async def set_knowledge(
        self,
        *,
        agent_id: str,
        value: str,
    ) -> LettaKnowledgeResult: ...

    async def set_agent_tools(
        self,
        *,
        agent_id: str,
        tool_ids: Sequence[str],
    ) -> None: ...

    async def disable_shared_memory_tools(
        self,
        *,
        agent_id: str,
    ) -> None: ...

    async def interact(
        self,
        *,
        agent_id: str,
        message: str,
    ) -> LettaInteractionResult: ...

    async def interact_in_conversation(
        self,
        *,
        agent_id: str,
        conversation_id: str,
        message: str,
    ) -> LettaInteractionResult: ...
