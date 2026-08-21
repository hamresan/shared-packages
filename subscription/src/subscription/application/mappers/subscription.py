from subscription.application.contracts import Clock, IdentifierGenerator
from subscription.application.dto import CreateSubscriptionCommand
from subscription.domain import Plan, Subscription, SubscriptionStatus


class CreateSubscriptionMapper:
    def __init__(
        self,
        identifier_generator: IdentifierGenerator,
        clock: Clock,
    ) -> None:
        self._identifier_generator = identifier_generator
        self._clock = clock

    def map(self, command: CreateSubscriptionCommand, plan: Plan) -> Subscription:
        return Subscription(
            id=self._identifier_generator.new_id(),
            subject=command.subject,
            plan_id=plan.id,
            subscription_type=plan.subscription_type,
            source=command.source,
            status=SubscriptionStatus.PENDING,
            created_at=self._clock.now(),
            trial_policy=command.trial_policy,
        )
