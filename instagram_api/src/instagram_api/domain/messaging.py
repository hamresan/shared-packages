"""Normalized Instagram messaging models."""

from dataclasses import dataclass
from datetime import datetime

from .identifiers import (
    InstagramConversationId,
    InstagramMessageId,
    InstagramUserId,
)


@dataclass(frozen=True, slots=True)
class InstagramConversation:
    """A conversation scoped to one selected Instagram connection."""

    id: InstagramConversationId
    participant_ids: tuple[InstagramUserId, ...]
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class InstagramMessage:
    """A provider-neutral Instagram message."""

    id: InstagramMessageId
    conversation_id: InstagramConversationId
    sender_id: InstagramUserId | None
    sent_at: datetime
    text: str | None = None
    is_unsupported: bool = False
    details_available: bool = True


@dataclass(frozen=True, slots=True)
class InstagramMessageSendRequest:
    """Normalized outbound message request."""

    recipient_id: InstagramUserId
    text: str


@dataclass(frozen=True, slots=True)
class InstagramMessageSendResult:
    """Normalized result returned after an outbound message is accepted."""

    message_id: InstagramMessageId
