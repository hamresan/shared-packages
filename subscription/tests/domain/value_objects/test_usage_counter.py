import pytest

from subscription import UsageCounter, UsageMetric, UsagePeriod


def test_usage_counter_accepts_zero_consumption() -> None:
    counter = UsageCounter(UsageMetric("conversations"), UsagePeriod.WEEK, 0)

    assert counter.consumed == 0


@pytest.mark.parametrize("consumed", [-1, True])
def test_usage_counter_rejects_invalid_consumption(consumed: int) -> None:
    with pytest.raises(ValueError, match="non-negative integer"):
        UsageCounter(UsageMetric("conversations"), UsagePeriod.WEEK, consumed)
