from dataclasses import dataclass

from subscription.domain.enums.trial import TrialCompletionMode
from subscription.domain.value_objects.trial_conditions import TimeCondition, UsageCondition


@dataclass(frozen=True, slots=True)
class TrialPolicy:
    """Defines the conditions that complete a trial."""

    completion_mode: TrialCompletionMode
    time_condition: TimeCondition | None = None
    usage_conditions: tuple[UsageCondition, ...] = ()

    def __post_init__(self) -> None:
        if self.time_condition is None and not self.usage_conditions:
            raise ValueError("trial policy must contain at least one condition")

        condition_keys = [
            (condition.metric.key, condition.period) for condition in self.usage_conditions
        ]
        if len(condition_keys) != len(set(condition_keys)):
            raise ValueError("trial usage conditions must be unique by metric and period")
