from datetime import timedelta

import pytest

from subscription import TimeCondition, UsageCondition, UsageMetric, UsagePeriod


def test_time_condition_accepts_positive_duration() -> None:
    condition = TimeCondition(timedelta(days=14))

    assert condition.max_duration == timedelta(days=14)


@pytest.mark.parametrize("duration", [timedelta(0), timedelta(seconds=-1)])
def test_time_condition_rejects_non_positive_duration(duration: timedelta) -> None:
    with pytest.raises(ValueError, match="duration"):
        TimeCondition(duration)


def test_usage_condition_defaults_to_trial_period() -> None:
    condition = UsageCondition(metric=UsageMetric("conversations"), limit=100)

    assert condition.period is UsagePeriod.TRIAL


@pytest.mark.parametrize("limit", [0, -1, True])
def test_usage_condition_rejects_non_positive_limit(limit: int) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        UsageCondition(metric=UsageMetric("conversations"), limit=limit)
