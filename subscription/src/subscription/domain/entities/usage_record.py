from dataclasses import dataclass
from datetime import datetime

from subscription.domain.value_objects.subject_reference import SubjectReference
from subscription.domain.value_objects.usage_metric import UsageMetric


@dataclass(frozen=True, slots=True)
class UsageRecord:
    """Immutable usage event recorded for a subscription subject."""

    subject: SubjectReference
    metric: UsageMetric
    amount: int
    occurred_at: datetime

    def __post_init__(self) -> None:
        if isinstance(self.amount, bool) or self.amount <= 0:
            raise ValueError("usage record amount must be a positive integer")
        if self.occurred_at.tzinfo is None or self.occurred_at.utcoffset() is None:
            raise ValueError("usage record occurred_at must be timezone-aware")
