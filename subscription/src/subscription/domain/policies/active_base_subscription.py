from collections.abc import Iterable

from subscription.domain.entities.subscription import Subscription
from subscription.domain.enums.subscription import SubscriptionStatus, SubscriptionType


class ActiveBaseSubscriptionPolicy:
    """Prevents a subject from occupying more than one BASE subscription slot."""

    def ensure_available(
        self,
        candidate: Subscription,
        current_subscriptions: Iterable[Subscription],
    ) -> None:
        if candidate.subscription_type is SubscriptionType.ADDON:
            return

        occupying_statuses = {
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.TRIALING,
        }
        for existing in current_subscriptions:
            if existing.id == candidate.id:
                continue
            if existing.subject != candidate.subject:
                continue
            if existing.subscription_type is not SubscriptionType.BASE:
                continue
            if existing.status in occupying_statuses:
                raise ValueError("subject already has an active BASE subscription")
