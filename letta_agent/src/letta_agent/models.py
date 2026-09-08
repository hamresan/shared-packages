from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LettaAgentSpec:
    name: str
    model: str
    persona: str


@dataclass(frozen=True, slots=True)
class LettaCreatedAgent:
    agent_id: str


@dataclass(frozen=True, slots=True)
class LettaCreatedConversation:
    conversation_id: str


@dataclass(frozen=True, slots=True)
class LettaIdentitySpec:
    identifier_key: str
    name: str


@dataclass(frozen=True, slots=True)
class LettaIdentity:
    identity_id: str
    identifier_key: str
    name: str


@dataclass(frozen=True, slots=True)
class LettaInteractionResult:
    succeeded: bool
    reply_text: str | None = None


@dataclass(frozen=True, slots=True)
class LettaKnowledgeResult:
    block_id: str
