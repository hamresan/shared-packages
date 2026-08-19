from dataclasses import dataclass

from subscription.domain.enums.usage import UsagePeriod
from subscription.domain.value_objects.usage_metric import UsageMetric


@dataclass(frozen=True, slots=True)
class UsageSnapshot:
    """Current consumed amount for one metric and usage period."""

    metric: UsageMetric
    period: UsagePeriod
    consumed: int

    def __post_init__(self) -> None:
        if isinstance(self.consumed, bool) or self.consumed < 0:
            raise ValueError("usage snapshot consumed amount must be a non-negative integer")
