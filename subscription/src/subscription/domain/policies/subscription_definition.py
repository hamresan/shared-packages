from subscription.domain.entities.subscription import Subscription
from subscription.domain.enums.subscription import SubscriptionStatus
from subscription.domain.policies.timezone_aware_datetime import (
    TimezoneAwareDatetimeValidator,
)


class SubscriptionDefinitionPolicy:
    """Validates invariants of a Subscription snapshot."""

    def __init__(self, datetime_validator: TimezoneAwareDatetimeValidator) -> None:
        self._datetime_validator = datetime_validator

    def validate(self, subscription: Subscription) -> None:
        timestamps = (
            (subscription.created_at, "created_at"),
            (subscription.started_at, "started_at"),
            (subscription.expires_at, "expires_at"),
            (subscription.trial_started_at, "trial_started_at"),
            (subscription.cancelled_at, "cancelled_at"),
            (subscription.expired_at, "expired_at"),
        )
        for value, field_name in timestamps:
            if value is not None:
                self._datetime_validator.validate(value, field_name)

        if (
            subscription.started_at is not None
            and subscription.started_at < subscription.created_at
        ):
            raise ValueError("started_at must not be before created_at")
        if subscription.expires_at is not None and subscription.started_at is not None:
            if subscription.expires_at <= subscription.started_at:
                raise ValueError("expires_at must be after started_at")
        if subscription.trial_started_at is not None:
            if subscription.trial_policy is None:
                raise ValueError("trial_started_at requires trial_policy")
            if subscription.trial_started_at < subscription.created_at:
                raise ValueError("trial_started_at must not be before created_at")
        if subscription.cancelled_at is not None:
            if subscription.cancelled_at < subscription.created_at:
                raise ValueError("cancelled_at must not be before created_at")
            if (
                subscription.started_at is not None
                and subscription.cancelled_at < subscription.started_at
            ):
                raise ValueError("cancelled_at must not be before started_at")
        if subscription.expired_at is not None:
            if subscription.expired_at < subscription.created_at:
                raise ValueError("expired_at must not be before created_at")
            if (
                subscription.started_at is not None
                and subscription.expired_at < subscription.started_at
            ):
                raise ValueError("expired_at must not be before started_at")

        started_statuses = {
            SubscriptionStatus.TRIALING,
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.EXPIRED,
        }
        if subscription.status in started_statuses and subscription.started_at is None:
            raise ValueError(f"{subscription.status} subscription requires started_at")

        if subscription.status is SubscriptionStatus.TRIALING:
            if subscription.trial_policy is None or subscription.trial_started_at is None:
                raise ValueError("trialing subscription requires trial_policy and trial_started_at")

        if (
            subscription.status is SubscriptionStatus.CANCELLED
            and subscription.cancelled_at is None
        ):
            raise ValueError("cancelled subscription requires cancelled_at")

        if (
            subscription.status is SubscriptionStatus.EXPIRED
            and subscription.expired_at is None
        ):
            raise ValueError("expired subscription requires expired_at")
