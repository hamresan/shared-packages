import pytest

from subscription import UsageMetric


def test_usage_metric_accepts_consumer_defined_key() -> None:
    metric = UsageMetric("conversations.weekly")

    assert metric.key == "conversations.weekly"


@pytest.mark.parametrize(
    "key",
    ["", "Conversations", "conversation usage", ".conversations", "conversations.", "a" * 121],
)
def test_usage_metric_rejects_non_canonical_key(key: str) -> None:
    with pytest.raises(ValueError, match="usage metric"):
        UsageMetric(key)
