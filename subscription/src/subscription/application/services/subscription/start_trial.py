from uuid import UUID

from subscription.application.contracts import Clock, SubscriptionUnitOfWorkFactory
from subscription.application.errors import SubscriptionNotFoundError
from subscription.domain import (
    ActiveBaseSubscriptionPolicy,
    Subscription,
    SubscriptionLifecycleService,
)


class StartTrialService:
    def __init__(
        self,
        unit_of_work_factory: SubscriptionUnitOfWorkFactory,
        clock: Clock,
        lifecycle_service: SubscriptionLifecycleService,
        active_base_policy: ActiveBaseSubscriptionPolicy,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock
        self._lifecycle_service = lifecycle_service
        self._active_base_policy = active_base_policy

    async def execute(self, subscription_id: UUID) -> Subscription:
        async with self._unit_of_work_factory() as unit_of_work:
            subscription = await unit_of_work.subscriptions.get_by_id(subscription_id)
            if subscription is None:
                raise SubscriptionNotFoundError(str(subscription_id))
            updated = self._lifecycle_service.start_trial(subscription, self._clock.now())
            current = await unit_of_work.subscriptions.list_for_subject(updated.subject)
            self._active_base_policy.ensure_available(updated, current)
            await unit_of_work.subscriptions.save(updated)
            await unit_of_work.commit()
        return updated
