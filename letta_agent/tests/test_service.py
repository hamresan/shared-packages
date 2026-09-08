import asyncio
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
from letta_agent.service import LettaAgentService


class FakeLettaGateway(LettaGateway):
    def __init__(self) -> None:
        self.created_specs: list[LettaAgentSpec] = []
        self.knowledge_updates: list[tuple[str, str]] = []
        self.agent_tool_updates: list[tuple[str, tuple[str, ...]]] = []
        self.shared_memory_tool_disables: list[str] = []
        self.interactions: list[tuple[str, str, str | None]] = []
        self.conversation_creations: list[str] = []
        self.identity_upserts: list[LettaIdentitySpec] = []
        self.identity_attachments: list[tuple[str, str]] = []
        self.conversation_interactions: list[tuple[str, str, str, str | None]] = []

    async def create_agent(self, spec: LettaAgentSpec) -> LettaCreatedAgent:
        self.created_specs.append(spec)
        return LettaCreatedAgent(agent_id="agent-1")

    async def create_conversation(
        self,
        *,
        agent_id: str,
    ) -> LettaCreatedConversation:
        self.conversation_creations.append(agent_id)
        return LettaCreatedConversation(conversation_id="conversation-1")

    async def upsert_identity(self, spec: LettaIdentitySpec) -> LettaIdentity:
        self.identity_upserts.append(spec)
        return LettaIdentity(
            identity_id="identity-1",
            identifier_key=spec.identifier_key,
            name=spec.name,
        )

    async def attach_identity(
        self,
        *,
        agent_id: str,
        identity_id: str,
    ) -> None:
        self.identity_attachments.append((agent_id, identity_id))

    async def set_knowledge(
        self,
        *,
        agent_id: str,
        value: str,
    ) -> LettaKnowledgeResult:
        self.knowledge_updates.append((agent_id, value))
        return LettaKnowledgeResult(block_id="block-1")

    async def set_agent_tools(
        self,
        *,
        agent_id: str,
        tool_ids: Sequence[str],
    ) -> None:
        self.agent_tool_updates.append((agent_id, tuple(tool_ids)))

    async def disable_shared_memory_tools(
        self,
        *,
        agent_id: str,
    ) -> None:
        self.shared_memory_tool_disables.append(agent_id)

    async def interact(
        self,
        *,
        agent_id: str,
        message: str,
        sender_id: str | None = None,
    ) -> LettaInteractionResult:
        self.interactions.append((agent_id, message, sender_id))
        return LettaInteractionResult(succeeded=True)

    async def interact_in_conversation(
        self,
        *,
        agent_id: str,
        conversation_id: str,
        message: str,
        sender_id: str | None = None,
    ) -> LettaInteractionResult:
        self.conversation_interactions.append((agent_id, conversation_id, message, sender_id))
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
    conversation = asyncio.run(service.create_conversation(agent_id=created.agent_id))
    asyncio.run(service.set_agent_tools(agent_id=created.agent_id, tool_ids=()))
    asyncio.run(service.disable_shared_memory_tools(agent_id=created.agent_id))
    interaction = asyncio.run(service.interact(agent_id=created.agent_id, message="Are you ready?"))
    conversation_interaction = asyncio.run(
        service.interact_in_conversation(
            agent_id=created.agent_id,
            conversation_id=conversation.conversation_id,
            message="What did I ask before?",
        )
    )

    assert created.agent_id == "agent-1"
    assert conversation.conversation_id == "conversation-1"
    assert knowledge.block_id == "block-1"
    assert interaction.succeeded is True
    assert conversation_interaction.succeeded is True
    assert gateway.created_specs == [spec]
    assert gateway.knowledge_updates == [("agent-1", "Account knowledge")]
    assert gateway.agent_tool_updates == [("agent-1", ())]
    assert gateway.shared_memory_tool_disables == ["agent-1"]
    assert gateway.interactions == [("agent-1", "Are you ready?", None)]
    assert gateway.conversation_creations == ["agent-1"]
    assert gateway.conversation_interactions == [
        ("agent-1", "conversation-1", "What did I ask before?", None)
    ]


def test_service_delegates_sender_identity_to_interactions() -> None:
    gateway = FakeLettaGateway()
    service = LettaAgentService(gateway)

    asyncio.run(
        service.interact(
            agent_id="agent-1",
            message="Hello",
            sender_id="identity-customer-1",
        )
    )
    asyncio.run(
        service.interact_in_conversation(
            agent_id="agent-1",
            conversation_id="conversation-1",
            message="Do you remember me?",
            sender_id="identity-customer-1",
        )
    )

    assert gateway.interactions == [("agent-1", "Hello", "identity-customer-1")]
    assert gateway.conversation_interactions == [
        (
            "agent-1",
            "conversation-1",
            "Do you remember me?",
            "identity-customer-1",
        )
    ]


def test_service_delegates_identity_lifecycle() -> None:
    gateway = FakeLettaGateway()
    service = LettaAgentService(gateway)
    spec = LettaIdentitySpec(
        identifier_key="business-1:customer-1",
        name="Instagram customer",
    )

    identity = asyncio.run(service.upsert_identity(spec))
    asyncio.run(
        service.attach_identity(
            agent_id="agent-1",
            identity_id=identity.identity_id,
        )
    )

    assert identity == LettaIdentity(
        identity_id="identity-1",
        identifier_key="business-1:customer-1",
        name="Instagram customer",
    )
    assert gateway.identity_upserts == [spec]
    assert gateway.identity_attachments == [("agent-1", "identity-1")]
