"""Provider DTOs for Meta Instagram conversations and messages."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MetaInstagramConversationDto:
    id: str
    updated_time: str | None


@dataclass(frozen=True, slots=True)
class MetaInstagramMessageSummaryDto:
    id: str
    created_time: str
    is_unsupported: bool


@dataclass(frozen=True, slots=True)
class MetaInstagramMessageDetailDto:
    id: str
    created_time: str
    sender_id: str | None
    message: str | None
