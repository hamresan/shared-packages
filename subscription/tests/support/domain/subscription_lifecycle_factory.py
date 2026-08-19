from subscription import (
    SubscriptionDefinitionValidator,
    SubscriptionLifecycleService,
    SubscriptionStateValidator,
    SubscriptionStatusTransitionPolicy,
    SubscriptionTimelineValidator,
    TimestampOrderValidator,
    TimezoneAwareDatetimeValidator,
)


def build_subscription_lifecycle_service() -> SubscriptionLifecycleService:
    datetime_validator = TimezoneAwareDatetimeValidator()
    definition_validator = SubscriptionDefinitionValidator(
        timeline_validator=SubscriptionTimelineValidator(
            datetime_validator=datetime_validator,
            timestamp_order_validator=TimestampOrderValidator(),
        ),
        state_validator=SubscriptionStateValidator(),
    )
    return SubscriptionLifecycleService(
        transition_policy=SubscriptionStatusTransitionPolicy(),
        definition_validator=definition_validator,
        datetime_validator=datetime_validator,
    )
