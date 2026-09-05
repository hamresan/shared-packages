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
class LettaInteractionResult:
    succeeded: bool


@dataclass(frozen=True, slots=True)
class LettaKnowledgeResult:
    block_id: str
    reply_text: str | None = None
