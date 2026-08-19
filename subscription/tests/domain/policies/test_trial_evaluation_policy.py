from datetime import timedelta

import pytest

from subscription import (
    TimeCondition,
    TrialCompletionMode,
    TrialEvaluationPolicy,
    TrialPolicy,
    UsageCondition,
    UsageCounter,
    UsageMetric,
    UsagePeriod,
)


def test_time_only_trial_completes_at_duration_limit() -> None:
    policy = TrialPolicy(
        completion_mode=TrialCompletionMode.ANY,
        time_condition=TimeCondition(timedelta(days=14)),
    )

    assert TrialEvaluationPolicy().is_complete(policy, elapsed=timedelta(days=14))


def test_usage_only_trial_completes_at_usage_limit() -> None:
    metric = UsageMetric("conversations")
    policy = TrialPolicy(
        completion_mode=TrialCompletionMode.ANY,
        usage_conditions=(UsageCondition(metric=metric, limit=100),),
    )

    assert TrialEvaluationPolicy().is_complete(
        policy,
        elapsed=timedelta(days=1),
        usage_counters=(UsageCounter(metric, UsagePeriod.TRIAL, 100),),
    )


def test_any_trial_completes_when_first_condition_is_met() -> None:
    metric = UsageMetric("conversations")
    policy = TrialPolicy(
        completion_mode=TrialCompletionMode.ANY,
        time_condition=TimeCondition(timedelta(days=14)),
        usage_conditions=(UsageCondition(metric=metric, limit=100),),
    )

    assert TrialEvaluationPolicy().is_complete(
        policy,
        elapsed=timedelta(days=3),
        usage_counters=(UsageCounter(metric, UsagePeriod.TRIAL, 100),),
    )


def test_all_trial_requires_all_conditions() -> None:
    metric = UsageMetric("conversations")
    policy = TrialPolicy(
        completion_mode=TrialCompletionMode.ALL,
        time_condition=TimeCondition(timedelta(days=14)),
        usage_conditions=(UsageCondition(metric=metric, limit=100),),
    )

    assert not TrialEvaluationPolicy().is_complete(
        policy,
        elapsed=timedelta(days=14),
        usage_counters=(UsageCounter(metric, UsagePeriod.TRIAL, 99),),
    )


def test_weekly_usage_condition_uses_matching_period_only() -> None:
    metric = UsageMetric("conversations")
    policy = TrialPolicy(
        completion_mode=TrialCompletionMode.ANY,
        usage_conditions=(
            UsageCondition(metric=metric, limit=50, period=UsagePeriod.WEEK),
        ),
    )

    assert not TrialEvaluationPolicy().is_complete(
        policy,
        elapsed=timedelta(days=2),
        usage_counters=(UsageCounter(metric, UsagePeriod.TRIAL, 60),),
    )
    assert TrialEvaluationPolicy().is_complete(
        policy,
        elapsed=timedelta(days=2),
        usage_counters=(UsageCounter(metric, UsagePeriod.WEEK, 50),),
    )


def test_trial_evaluation_rejects_negative_elapsed_time() -> None:
    policy = TrialPolicy(
        completion_mode=TrialCompletionMode.ANY,
        time_condition=TimeCondition(timedelta(days=1)),
    )

    with pytest.raises(ValueError, match="must not be negative"):
        TrialEvaluationPolicy().is_complete(policy, elapsed=timedelta(seconds=-1))
