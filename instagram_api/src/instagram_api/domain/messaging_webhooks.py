"""Normalized Instagram messaging webhook models."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .identifiers import InstagramMessageId, InstagramUserId


class InstagramMessagingWebhookPayload:
    """Marker base for normalized Instagram messaging webhook payloads."""


class InstagramMessageReactionAction(StrEnum):
    """Normalized reaction actions."""

    REACT = "react"
    UNREACT = "unreact"


@dataclass(frozen=True, slots=True)
class InstagramInboundMessageAttachment:
    """Normalized inbound message attachment metadata."""

    attachment_type: str | None
    url: str | None


@dataclass(frozen=True, slots=True)
class InstagramMessageReceived(InstagramMessagingWebhookPayload):
    """Normalized inbound Instagram direct message."""

    sender_id: InstagramUserId
    recipient_id: InstagramUserId
    occurred_at: datetime
    message_id: InstagramMessageId
    text: str | None = None
    attachments: tuple[InstagramInboundMessageAttachment, ...] = ()
    is_echo: bool = False
    is_self: bool = False
    is_deleted: bool = False
    is_unsupported: bool = False
    reply_to_story_id: str | None = None
    reply_to_story_url: str | None = None


@dataclass(frozen=True, slots=True)
class InstagramMessagePostbackReceived(InstagramMessagingWebhookPayload):
    """Normalized messaging postback event."""

    sender_id: InstagramUserId
    recipient_id: InstagramUserId
    occurred_at: datetime
    message_id: InstagramMessageId
    title: str | None
    payload: str | None


@dataclass(frozen=True, slots=True)
class InstagramMessageRead(InstagramMessagingWebhookPayload):
    """Normalized message-read event."""

    sender_id: InstagramUserId
    recipient_id: InstagramUserId
    occurred_at: datetime
    message_id: InstagramMessageId


@dataclass(frozen=True, slots=True)
class InstagramMessageReaction(InstagramMessagingWebhookPayload):
    """Normalized message-reaction event."""

    sender_id: InstagramUserId
    recipient_id: InstagramUserId
    occurred_at: datetime
    message_id: InstagramMessageId
    action: InstagramMessageReactionAction
    reaction: str | None
    emoji: str | None


@dataclass(frozen=True, slots=True)
class InstagramMessageEdited(InstagramMessagingWebhookPayload):
    """Normalized message-edit event."""

    sender_id: InstagramUserId
    recipient_id: InstagramUserId
    occurred_at: datetime
    message_id: InstagramMessageId
    text: str | None
    edit_count: int | None


@dataclass(frozen=True, slots=True)
class InstagramMessagingReferralReceived(InstagramMessagingWebhookPayload):
    """Normalized messaging referral event."""

    sender_id: InstagramUserId
    recipient_id: InstagramUserId
    occurred_at: datetime
    referral_ref: str | None
    source: str | None
    referral_type: str | None
