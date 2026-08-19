from subscription.domain.entities.subscription import Subscription
from subscription.domain.enums.subscription import SubscriptionStatus

_REQUIRED_FIELDS_BY_STATUS: dict[SubscriptionStatus, tuple[str, ...]] = {
    SubscriptionStatus.TRIALING: ("started_at", "trial_policy", "trial_started_at"),
    SubscriptionStatus.ACTIVE: ("started_at",),
    SubscriptionStatus.CANCELLED: ("cancelled_at",),
    SubscriptionStatus.EXPIRED: ("started_at", "expired_at"),
}


class SubscriptionStateValidator:
    """Validates status-specific subscription state requirements."""

    def validate(self, subscription: Subscription) -> None:
        for field_name in _REQUIRED_FIELDS_BY_STATUS.get(subscription.status, ()):
            if getattr(subscription, field_name) is None:
                raise ValueError(f"{subscription.status} subscription requires {field_name}")

        if subscription.trial_started_at is not None and subscription.trial_policy is None:
            raise ValueError("trial_started_at requires trial_policy")
