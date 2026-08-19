from subscription import (
    SubscriptionDefinitionValidator,
    SubscriptionStateValidator,
    SubscriptionTimelineValidator,
    TimestampOrderValidator,
    TimezoneAwareDatetimeValidator,
)


def build_subscription_definition_validator() -> SubscriptionDefinitionValidator:
    datetime_validator = TimezoneAwareDatetimeValidator()
    return SubscriptionDefinitionValidator(
        timeline_validator=SubscriptionTimelineValidator(
            datetime_validator=datetime_validator,
            timestamp_order_validator=TimestampOrderValidator(),
        ),
        state_validator=SubscriptionStateValidator(),
    )
