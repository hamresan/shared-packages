from dataclasses import dataclass

from subscription.domain import SubjectReference, UsageMetric, UsagePeriod


@dataclass(frozen=True, slots=True)
class RecordUsageCommand:
    subject: SubjectReference
    metric: UsageMetric
    amount: int = 1
    idempotency_key: str | None = None


@dataclass(frozen=True, slots=True)
class GetUsageCounterQuery:
    subject: SubjectReference
    metric: UsageMetric
    period: UsagePeriod
