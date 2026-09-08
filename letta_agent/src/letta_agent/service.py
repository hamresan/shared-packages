from collections.abc import Sequence

from letta_agent.contracts import LettaGateway
from letta_agent.models import (
    LettaAgentSpec,
    LettaCreatedAgent,
    LettaCreatedConversation,
    LettaIdentity,
    LettaIdentitySpec,
    LettaInteractionResult,
    LettaKnowledgeResult,
)


class LettaAgentService:
    def __init__(self, gateway: LettaGateway) -> None:
        self._gateway = gateway

    async def create(self, spec: LettaAgentSpec) -> LettaCreatedAgent:
        return await self._gateway.create_agent(spec)

    async def create_conversation(
        self,
        *,
        agent_id: str,
    ) -> LettaCreatedConversation:
        return await self._gateway.create_conversation(agent_id=agent_id)

    async def upsert_identity(self, spec: LettaIdentitySpec) -> LettaIdentity:
        return await self._gateway.upsert_identity(spec)

    async def attach_identity(
        self,
        *,
        agent_id: str,
        identity_id: str,
    ) -> None:
        await self._gateway.attach_identity(
            agent_id=agent_id,
            identity_id=identity_id,
        )

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

    async def set_agent_tools(
        self,
        *,
        agent_id: str,
        tool_ids: Sequence[str],
    ) -> None:
        await self._gateway.set_agent_tools(
            agent_id=agent_id,
            tool_ids=tool_ids,
        )

    async def disable_shared_memory_tools(
        self,
        *,
        agent_id: str,
    ) -> None:
        await self._gateway.disable_shared_memory_tools(agent_id=agent_id)

    async def interact(
        self,
        *,
        agent_id: str,
        message: str,
        sender_id: str | None = None,
    ) -> LettaInteractionResult:
        return await self._gateway.interact(
            agent_id=agent_id,
            message=message,
            sender_id=sender_id,
        )

    async def interact_in_conversation(
        self,
        *,
        agent_id: str,
        conversation_id: str,
        message: str,
        sender_id: str | None = None,
    ) -> LettaInteractionResult:
        return await self._gateway.interact_in_conversation(
            agent_id=agent_id,
            conversation_id=conversation_id,
            message=message,
            sender_id=sender_id,
        )
