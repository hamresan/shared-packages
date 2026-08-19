from collections.abc import Callable

from subscription.domain.entities.subscription import Subscription
from subscription.domain.enums.subscription import SubscriptionStatus

type SubscriptionFieldReader = Callable[[Subscription], object | None]
type RequiredField = tuple[str, SubscriptionFieldReader]

_REQUIRED_FIELDS_BY_STATUS: dict[SubscriptionStatus, tuple[RequiredField, ...]] = {
    SubscriptionStatus.TRIALING: (
        ("started_at", lambda subscription: subscription.started_at),
        ("trial_policy", lambda subscription: subscription.trial_policy),
        ("trial_started_at", lambda subscription: subscription.trial_started_at),
    ),
    SubscriptionStatus.ACTIVE: (
        ("started_at", lambda subscription: subscription.started_at),
    ),
    SubscriptionStatus.CANCELLED: (
        ("cancelled_at", lambda subscription: subscription.cancelled_at),
    ),
    SubscriptionStatus.EXPIRED: (
        ("started_at", lambda subscription: subscription.started_at),
        ("expired_at", lambda subscription: subscription.expired_at),
    ),
}


class SubscriptionStateValidator:
    """Validates status-specific subscription state requirements."""

    def validate(self, subscription: Subscription) -> None:
        for field_name, reader in _REQUIRED_FIELDS_BY_STATUS.get(subscription.status, ()):
            if reader(subscription) is None:
                raise ValueError(f"{subscription.status} subscription requires {field_name}")

        if subscription.trial_started_at is not None and subscription.trial_policy is None:
            raise ValueError("trial_started_at requires trial_policy")
