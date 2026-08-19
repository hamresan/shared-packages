import pytest

from subscription import EntitlementKey


@pytest.mark.parametrize(
    "key",
    ["analytics.advanced", "team.members_max", "ai-messages.monthly", "products"],
)
def test_entitlement_key_accepts_canonical_dotted_identifiers(key: str) -> None:
    assert EntitlementKey(key).value == key


@pytest.mark.parametrize(
    "key", ["", ".analytics", "Analytics.advanced", "team..max", "team members"]
)
def test_entitlement_key_rejects_invalid_identifiers(key: str) -> None:
    with pytest.raises(ValueError, match="entitlement key"):
        EntitlementKey(key)


def test_entitlement_key_rejects_values_longer_than_128_characters() -> None:
    with pytest.raises(ValueError, match="128"):
        EntitlementKey("a" * 129)
