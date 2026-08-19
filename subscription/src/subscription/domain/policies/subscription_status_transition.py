from subscription.domain.enums.subscription import SubscriptionStatus


class SubscriptionStatusTransitionPolicy:
    """Owns the allowed lifecycle status transitions."""

    _ALLOWED_TRANSITIONS: dict[SubscriptionStatus, frozenset[SubscriptionStatus]] = {
        SubscriptionStatus.PENDING: frozenset(
            {
                SubscriptionStatus.TRIALING,
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.CANCELLED,
            }
        ),
        SubscriptionStatus.TRIALING: frozenset(
            {
                SubscriptionStatus.ACTIVE,
                SubscriptionStatus.CANCELLED,
                SubscriptionStatus.EXPIRED,
            }
        ),
        SubscriptionStatus.ACTIVE: frozenset(
            {
                SubscriptionStatus.CANCELLED,
                SubscriptionStatus.EXPIRED,
            }
        ),
        SubscriptionStatus.EXPIRED: frozenset({SubscriptionStatus.ACTIVE}),
        SubscriptionStatus.CANCELLED: frozenset(),
    }

    def ensure_allowed(
        self,
        current: SubscriptionStatus,
        target: SubscriptionStatus,
    ) -> None:
        if target not in self._ALLOWED_TRANSITIONS[current]:
            raise ValueError(f"subscription status transition {current} -> {target} is not allowed")
