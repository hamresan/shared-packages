import asyncio

from letta_agent.contracts import LettaGateway
from letta_agent.models import (
    LettaAgentSpec,
    LettaCreatedAgent,
    LettaInteractionResult,
    LettaKnowledgeResult,
)
from letta_agent.service import LettaAgentService


class FakeLettaGateway(LettaGateway):
    def __init__(self) -> None:
        self.created_specs: list[LettaAgentSpec] = []
        self.knowledge_updates: list[tuple[str, str]] = []
        self.interactions: list[tuple[str, str]] = []

    async def create_agent(self, spec: LettaAgentSpec) -> LettaCreatedAgent:
        self.created_specs.append(spec)
        return LettaCreatedAgent(agent_id="agent-1")

    async def set_knowledge(
        self,
        *,
        agent_id: str,
        value: str,
    ) -> LettaKnowledgeResult:
        self.knowledge_updates.append((agent_id, value))
        return LettaKnowledgeResult(block_id="block-1")

    async def interact(
        self,
        *,
        agent_id: str,
        message: str,
    ) -> LettaInteractionResult:
        self.interactions.append((agent_id, message))
        return LettaInteractionResult(succeeded=True)


def test_service_delegates_agent_creation_and_interaction() -> None:
    gateway = FakeLettaGateway()
    service = LettaAgentService(gateway)
    spec = LettaAgentSpec(
        name="sellora-agent",
        model="openai/gpt-4.1",
        persona="Keep responses concise.",
    )

    created = asyncio.run(service.create(spec))
    knowledge = asyncio.run(
        service.set_knowledge(
            agent_id=created.agent_id,
            value="Account knowledge",
        )
    )
    interaction = asyncio.run(
        service.interact(agent_id=created.agent_id, message="Are you ready?")
    )

    assert created.agent_id == "agent-1"
    assert knowledge.block_id == "block-1"
    assert interaction.succeeded is True
    assert gateway.created_specs == [spec]
    assert gateway.knowledge_updates == [("agent-1", "Account knowledge")]
    assert gateway.interactions == [("agent-1", "Are you ready?")]
