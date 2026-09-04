"""Mappers for Meta Instagram conversation and message DTOs."""

from datetime import datetime

from instagram_api.domain import (
    InstagramConversation,
    InstagramConversationId,
    InstagramMessage,
    InstagramMessageId,
    InstagramUserId,
)
from instagram_api.infrastructure.meta.http import MetaInvalidResponseError

from .dto import (
    MetaInstagramConversationDto,
    MetaInstagramMessageDetailDto,
    MetaInstagramMessageSummaryDto,
)


class MetaInstagramMessagingMapper:
    """Maps typed provider DTOs to normalized domain models."""

    def conversation(self, dto: MetaInstagramConversationDto) -> InstagramConversation:
        updated_at = self._timestamp(dto.updated_time) if dto.updated_time is not None else None
        return InstagramConversation(
            id=InstagramConversationId(dto.id),
            participant_ids=(),
            updated_at=updated_at,
        )

    def message(
        self,
        conversation_id: InstagramConversationId,
        summary: MetaInstagramMessageSummaryDto,
        detail: MetaInstagramMessageDetailDto | None,
    ) -> InstagramMessage:
        sender_id = (
            InstagramUserId(detail.sender_id)
            if detail is not None and detail.sender_id is not None
            else None
        )
        return InstagramMessage(
            id=InstagramMessageId(summary.id),
            conversation_id=conversation_id,
            sender_id=sender_id,
            sent_at=self._timestamp(summary.created_time),
            text=detail.message if detail is not None else None,
            is_unsupported=summary.is_unsupported,
            details_available=detail is not None,
        )

    @staticmethod
    def _timestamp(value: str) -> datetime:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise MetaInvalidResponseError(
                message="Meta messaging payload contains an invalid timestamp.",
                status_code=200,
            ) from exc
