from subscription import (
    SubscriptionDefinitionValidator,
    SubscriptionStateValidator,
    SubscriptionTimelineValidator,
    TimestampOrderValidator,
    TimezoneAwareDatetimeValidator,
)


def build_subscription_timeline_validator() -> SubscriptionTimelineValidator:
    return SubscriptionTimelineValidator(
        datetime_validator=TimezoneAwareDatetimeValidator(),
        timestamp_order_validator=TimestampOrderValidator(),
    )


def build_subscription_definition_validator() -> SubscriptionDefinitionValidator:
    return SubscriptionDefinitionValidator(
        timeline_validator=build_subscription_timeline_validator(),
        state_validator=SubscriptionStateValidator(),
    )
