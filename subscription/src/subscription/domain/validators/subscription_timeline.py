from subscription.domain.entities.subscription import Subscription
from subscription.domain.validators.timestamp_order import TimestampOrderValidator
from subscription.domain.validators.timezone_aware_datetime import (
    TimezoneAwareDatetimeValidator,
)


class SubscriptionTimelineValidator:
    """Validates chronological consistency of subscription timestamps."""

    def __init__(
        self,
        datetime_validator: TimezoneAwareDatetimeValidator,
        timestamp_order_validator: TimestampOrderValidator,
    ) -> None:
        self._datetime_validator = datetime_validator
        self._timestamp_order_validator = timestamp_order_validator

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
            self._datetime_validator.validate_optional(value, field_name)

        self._timestamp_order_validator.ensure_not_before(
            subscription.started_at,
            subscription.created_at,
            "started_at",
            "created_at",
        )
        self._timestamp_order_validator.ensure_after(
            subscription.expires_at,
            subscription.started_at,
            "expires_at",
            "started_at",
        )
        self._timestamp_order_validator.ensure_not_before(
            subscription.trial_started_at,
            subscription.created_at,
            "trial_started_at",
            "created_at",
        )

        lifecycle_origin = subscription.started_at or subscription.created_at
        lifecycle_origin_name = (
            "started_at" if subscription.started_at is not None else "created_at"
        )
        self._timestamp_order_validator.ensure_not_before(
            subscription.cancelled_at,
            lifecycle_origin,
            "cancelled_at",
            lifecycle_origin_name,
        )
        self._timestamp_order_validator.ensure_not_before(
            subscription.expired_at,
            lifecycle_origin,
            "expired_at",
            lifecycle_origin_name,
        )
