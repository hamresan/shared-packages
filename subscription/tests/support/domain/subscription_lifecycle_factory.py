from subscription import (
    SubscriptionDefinitionPolicy,
    SubscriptionLifecycleService,
    SubscriptionStatusTransitionPolicy,
    TimezoneAwareDatetimeValidator,
)


def build_subscription_lifecycle_service() -> SubscriptionLifecycleService:
    datetime_validator = TimezoneAwareDatetimeValidator()
    return SubscriptionLifecycleService(
        transition_policy=SubscriptionStatusTransitionPolicy(),
        definition_policy=SubscriptionDefinitionPolicy(datetime_validator),
        datetime_validator=datetime_validator,
    )
