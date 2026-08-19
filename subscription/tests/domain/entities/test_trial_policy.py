import pytest

from subscription import (
    TrialCompletionMode,
    TrialPolicy,
    UsageCondition,
    UsageMetric,
    UsagePeriod,
)


def test_trial_policy_requires_at_least_one_condition() -> None:
    with pytest.raises(ValueError, match="at least one condition"):
        TrialPolicy(completion_mode=TrialCompletionMode.ANY)


def test_trial_policy_rejects_duplicate_usage_condition_identity() -> None:
    condition = UsageCondition(
        metric=UsageMetric("conversations"),
        limit=50,
        period=UsagePeriod.WEEK,
    )

    with pytest.raises(ValueError, match="unique"):
        TrialPolicy(
            completion_mode=TrialCompletionMode.ANY,
            usage_conditions=(condition, condition),
        )
