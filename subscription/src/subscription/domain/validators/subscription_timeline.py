from datetime import datetime

from subscription.domain.entities.subscription import Subscription
from subscription.domain.validators.timezone_aware_datetime import TimezoneAwareDatetimeValidator


class SubscriptionTimelineValidator:
    """Validates chronological consistency of subscription timestamps."""

    def __init__(self, datetime_validator: TimezoneAwareDatetimeValidator) -> None:
        self._datetime_validator = datetime_validator

    def validate(self, subscription: Subscription) -> None:
        self._validate_timestamps(subscription)
        self._ensure_not_before(subscription.started_at, subscription.created_at, "started_at", "created_at")
        self._ensure_after(subscription.expires_at, subscription.started_at, "expires_at", "started_at")
        self._ensure_not_before(
            subscription.trial_started_at,
            subscription.created_at,
            "trial_started_at",
            "created_at",
        )
        self._ensure_not_before(
            subscription.cancelled_at,
            subscription.started_at or subscription.created_at,
            "cancelled_at",
            "started_at" if subscription.started_at is not None else "created_at",
        )
        self._ensure_not_before(
            subscription.expired_at,
            subscription.started_at or subscription.created_at,
            "expired_at",
            "started_at" if subscription.started_at is not None else "created_at",
        )

    def _validate_timestamps(self, subscription: Subscription) -> None:
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

    @staticmethod
    def _ensure_not_before(
        value: datetime | None,
        minimum: datetime,
        field_name: str,
        minimum_field_name: str,
    ) -> None:
        if value is not None and value < minimum:
            raise ValueError(f"{field_name} must not be before {minimum_field_name}")

    @staticmethod
    def _ensure_after(
        value: datetime | None,
        minimum: datetime | None,
        field_name: str,
        minimum_field_name: str,
    ) -> None:
        if value is not None and minimum is not None and value <= minimum:
            raise ValueError(f"{field_name} must be after {minimum_field_name}")
