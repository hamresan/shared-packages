from datetime import timedelta

from subscription import (
    TimeCondition,
    TrialCompletionMode,
    TrialPolicy,
    UsageCondition,
    UsageMetric,
    UsagePeriod,
)


class TrialPolicyBuilder:
    def __init__(self) -> None:
        self._completion_mode = TrialCompletionMode.ANY
        self._time_condition: TimeCondition | None = TimeCondition(timedelta(days=14))
        self._usage_conditions: tuple[UsageCondition, ...] = ()

    def with_completion_mode(self, mode: TrialCompletionMode) -> "TrialPolicyBuilder":
        self._completion_mode = mode
        return self

    def without_time_condition(self) -> "TrialPolicyBuilder":
        self._time_condition = None
        return self

    def with_usage_condition(
        self,
        metric: str,
        limit: int,
        period: UsagePeriod = UsagePeriod.TRIAL,
    ) -> "TrialPolicyBuilder":
        self._usage_conditions = (
            UsageCondition(metric=UsageMetric(metric), limit=limit, period=period),
        )
        return self

    def with_usage_conditions(self, *conditions: UsageCondition) -> "TrialPolicyBuilder":
        self._usage_conditions = tuple(conditions)
        return self

    def build(self) -> TrialPolicy:
        return TrialPolicy(
            completion_mode=self._completion_mode,
            time_condition=self._time_condition,
            usage_conditions=self._usage_conditions,
        )
