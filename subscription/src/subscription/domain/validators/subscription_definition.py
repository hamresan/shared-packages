from subscription.domain.entities.subscription import Subscription
from subscription.domain.validators.subscription_state import SubscriptionStateValidator
from subscription.domain.validators.subscription_timeline import SubscriptionTimelineValidator


class SubscriptionDefinitionValidator:
    """Coordinates validation of a Subscription snapshot."""

    def __init__(
        self,
        timeline_validator: SubscriptionTimelineValidator,
        state_validator: SubscriptionStateValidator,
    ) -> None:
        self._timeline_validator = timeline_validator
        self._state_validator = state_validator

    def validate(self, subscription: Subscription) -> None:
        self._timeline_validator.validate(subscription)
        self._state_validator.validate(subscription)
