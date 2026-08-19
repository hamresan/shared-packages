from datetime import datetime

from subscription.domain.entities.subscription import Subscription
from subscription.domain.enums.subscription import SubscriptionStatus
from subscription.domain.policies.timezone_aware_datetime import (
    TimezoneAwareDatetimeValidator,
)


class SubscriptionValidityPolicy:
    """Evaluates whether one subscription is currently usable."""

    def __init__(self, datetime_validator: TimezoneAwareDatetimeValidator) -> None:
        self._datetime_validator = datetime_validator

    def is_valid(
        self,
        subscription: Subscription,
        at: datetime,
        *,
        trial_completed: bool = False,
    ) -> bool:
        self._datetime_validator.validate(at, "at")

        if subscription.status not in {
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.TRIALING,
        }:
            return False
        if subscription.started_at is None or at < subscription.started_at:
            return False
        if subscription.expires_at is not None and at >= subscription.expires_at:
            return False
        if subscription.status is SubscriptionStatus.TRIALING and trial_completed:
            return False
        return True
