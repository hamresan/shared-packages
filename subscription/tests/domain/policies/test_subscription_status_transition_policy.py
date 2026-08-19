import pytest

from subscription import SubscriptionStatus, SubscriptionStatusTransitionPolicy


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (SubscriptionStatus.PENDING, SubscriptionStatus.TRIALING),
        (SubscriptionStatus.PENDING, SubscriptionStatus.ACTIVE),
        (SubscriptionStatus.PENDING, SubscriptionStatus.CANCELLED),
        (SubscriptionStatus.TRIALING, SubscriptionStatus.ACTIVE),
        (SubscriptionStatus.TRIALING, SubscriptionStatus.CANCELLED),
        (SubscriptionStatus.TRIALING, SubscriptionStatus.EXPIRED),
        (SubscriptionStatus.ACTIVE, SubscriptionStatus.CANCELLED),
        (SubscriptionStatus.ACTIVE, SubscriptionStatus.EXPIRED),
        (SubscriptionStatus.EXPIRED, SubscriptionStatus.ACTIVE),
    ],
)
def test_subscription_status_transition_policy_accepts_allowed_transition(
    current: SubscriptionStatus,
    target: SubscriptionStatus,
) -> None:
    SubscriptionStatusTransitionPolicy().ensure_allowed(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING),
        (SubscriptionStatus.CANCELLED, SubscriptionStatus.ACTIVE),
        (SubscriptionStatus.EXPIRED, SubscriptionStatus.TRIALING),
        (SubscriptionStatus.PENDING, SubscriptionStatus.EXPIRED),
    ],
)
def test_subscription_status_transition_policy_rejects_disallowed_transition(
    current: SubscriptionStatus,
    target: SubscriptionStatus,
) -> None:
    with pytest.raises(ValueError, match="not allowed"):
        SubscriptionStatusTransitionPolicy().ensure_allowed(current, target)
