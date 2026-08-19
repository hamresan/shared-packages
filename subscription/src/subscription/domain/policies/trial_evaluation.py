from datetime import timedelta

from subscription.domain.entities.trial_policy import TrialPolicy
from subscription.domain.enums.trial import TrialCompletionMode
from subscription.domain.value_objects.usage_counter import UsageCounter


class TrialEvaluationPolicy:
    """Evaluates whether a trial has completed from supplied domain facts."""

    def is_complete(
        self,
        policy: TrialPolicy,
        *,
        elapsed: timedelta,
        usage_counters: tuple[UsageCounter, ...] = (),
    ) -> bool:
        if elapsed < timedelta(0):
            raise ValueError("trial elapsed duration must not be negative")

        results: list[bool] = []

        if policy.time_condition is not None:
            results.append(elapsed >= policy.time_condition.max_duration)

        for condition in policy.usage_conditions:
            consumed = 0
            for counter in usage_counters:
                if counter.metric == condition.metric and counter.period == condition.period:
                    consumed = counter.consumed
                    break
            results.append(consumed >= condition.limit)

        if policy.completion_mode is TrialCompletionMode.ANY:
            return any(results)
        return all(results)
