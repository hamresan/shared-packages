"""Eligibility policy for Instagram message-detail reads."""

from .dto import MetaInstagramMessageSummaryDto

META_MESSAGE_DETAIL_LIMIT = 20


class MetaInstagramMessageDetailAvailabilityPolicy:
    """Applies Meta's documented message-detail availability rules."""

    def can_read(
        self,
        summary: MetaInstagramMessageSummaryDto,
        position: int,
    ) -> bool:
        """Return whether a detail request should be attempted."""

        return not summary.is_unsupported and position < META_MESSAGE_DETAIL_LIMIT
