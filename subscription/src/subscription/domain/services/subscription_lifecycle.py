from dataclasses import replace
from datetime import datetime

from subscription.domain.entities.subscription import Subscription
from subscription.domain.enums.subscription import SubscriptionStatus
from subscription.domain.policies.subscription_definition import SubscriptionDefinitionPolicy
from subscription.domain.policies.subscription_status_transition import (
    SubscriptionStatusTransitionPolicy,
)
from subscription.domain.policies.timezone_aware_datetime import TimezoneAwareDatetimeValidator


class SubscriptionLifecycleService:
    """Applies lifecycle operations to immutable Subscription snapshots."""

    def __init__(
        self,
        transition_policy: SubscriptionStatusTransitionPolicy,
        definition_policy: SubscriptionDefinitionPolicy,
        datetime_validator: TimezoneAwareDatetimeValidator,
    ) -> None:
        self._transition_policy = transition_policy
        self._definition_policy = definition_policy
        self._datetime_validator = datetime_validator

    def start_trial(self, subscription: Subscription, at: datetime) -> Subscription:
        self._datetime_validator.validate(at, "at")
        self._transition_policy.ensure_allowed(subscription.status, SubscriptionStatus.TRIALING)
        if subscription.trial_policy is None:
            raise ValueError("subscription must have a trial_policy before starting a trial")

        result = replace(
            subscription,
            status=SubscriptionStatus.TRIALING,
            started_at=subscription.started_at or at,
            trial_started_at=at,
            cancelled_at=None,
            expired_at=None,
        )
        self._definition_policy.validate(result)
        return result

    def activate(
        self,
        subscription: Subscription,
        at: datetime,
        *,
        expires_at: datetime | None = None,
    ) -> Subscription:
        self._datetime_validator.validate(at, "at")
        if expires_at is not None:
            self._datetime_validator.validate(expires_at, "expires_at")
        self._transition_policy.ensure_allowed(subscription.status, SubscriptionStatus.ACTIVE)

        result = replace(
            subscription,
            status=SubscriptionStatus.ACTIVE,
            started_at=subscription.started_at or at,
            expires_at=expires_at if expires_at is not None else subscription.expires_at,
            cancelled_at=None,
            expired_at=None,
        )
        self._definition_policy.validate(result)
        return result

    def cancel(self, subscription: Subscription, at: datetime) -> Subscription:
        self._datetime_validator.validate(at, "at")
        self._transition_policy.ensure_allowed(subscription.status, SubscriptionStatus.CANCELLED)

        result = replace(
            subscription,
            status=SubscriptionStatus.CANCELLED,
            cancelled_at=at,
        )
        self._definition_policy.validate(result)
        return result

    def expire(self, subscription: Subscription, at: datetime) -> Subscription:
        self._datetime_validator.validate(at, "at")
        self._transition_policy.ensure_allowed(subscription.status, SubscriptionStatus.EXPIRED)

        result = replace(
            subscription,
            status=SubscriptionStatus.EXPIRED,
            expired_at=at,
        )
        self._definition_policy.validate(result)
        return result

    def extend(self, subscription: Subscription, new_expires_at: datetime) -> Subscription:
        self._datetime_validator.validate(new_expires_at, "new_expires_at")
        if subscription.status not in {SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING}:
            raise ValueError("only active or trialing subscriptions can be extended")
        if subscription.expires_at is not None and new_expires_at <= subscription.expires_at:
            raise ValueError("new_expires_at must be after the current expires_at")

        result = replace(subscription, expires_at=new_expires_at)
        self._definition_policy.validate(result)
        return result

    def renew(
        self,
        subscription: Subscription,
        at: datetime,
        new_expires_at: datetime,
    ) -> Subscription:
        self._datetime_validator.validate(at, "at")
        self._datetime_validator.validate(new_expires_at, "new_expires_at")
        if new_expires_at <= at:
            raise ValueError("new_expires_at must be after renewal time")

        if subscription.status is SubscriptionStatus.ACTIVE:
            return self.extend(subscription, new_expires_at)

        self._transition_policy.ensure_allowed(subscription.status, SubscriptionStatus.ACTIVE)
        result = replace(
            subscription,
            status=SubscriptionStatus.ACTIVE,
            started_at=subscription.started_at or at,
            expires_at=new_expires_at,
            expired_at=None,
            cancelled_at=None,
        )
        self._definition_policy.validate(result)
        return result
