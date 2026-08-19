from dataclasses import dataclass
from datetime import timedelta

from subscription.domain.enums.usage import UsagePeriod
from subscription.domain.value_objects.usage_metric import UsageMetric


@dataclass(frozen=True, slots=True)
class TimeCondition:
    """Trial condition completed after the configured duration."""

    max_duration: timedelta

    def __post_init__(self) -> None:
        if self.max_duration <= timedelta(0):
            raise ValueError("trial time condition duration must be positive")


@dataclass(frozen=True, slots=True)
class UsageCondition:
    """Trial condition completed when usage reaches the configured limit."""

    metric: UsageMetric
    limit: int
    period: UsagePeriod = UsagePeriod.TRIAL

    def __post_init__(self) -> None:
        if isinstance(self.limit, bool) or self.limit <= 0:
            raise ValueError("trial usage condition limit must be a positive integer")
