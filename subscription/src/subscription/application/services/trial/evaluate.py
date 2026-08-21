from uuid import UUID

from subscription.application.contracts import Clock, SubscriptionUnitOfWorkFactory
from subscription.application.errors import SubscriptionNotFoundError
from subscription.domain import TrialEvaluationPolicy


class EvaluateTrialService:
    def __init__(
        self,
        unit_of_work_factory: SubscriptionUnitOfWorkFactory,
        clock: Clock,
        evaluation_policy: TrialEvaluationPolicy,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock
        self._evaluation_policy = evaluation_policy

    async def execute(self, subscription_id: UUID) -> bool:
        async with self._unit_of_work_factory() as unit_of_work:
            subscription = await unit_of_work.subscriptions.get_by_id(subscription_id)
            if subscription is None:
                raise SubscriptionNotFoundError(str(subscription_id))
            if subscription.trial_policy is None or subscription.trial_started_at is None:
                return False

            now = self._clock.now()
            counters = tuple(
                [
                    await unit_of_work.usage.get_counter(
                        subscription.subject,
                        condition.metric,
                        condition.period,
                        now,
                    )
                    for condition in subscription.trial_policy.usage_conditions
                ]
            )

        elapsed = now - subscription.trial_started_at
        return self._evaluation_policy.is_complete(
            subscription.trial_policy,
            elapsed=elapsed,
            usage_counters=counters,
        )
