from uuid import UUID

from subscription.application.contracts import Clock, SubscriptionUnitOfWorkFactory
from subscription.application.errors import SubscriptionNotFoundError
from subscription.domain import Subscription, SubscriptionLifecycleService


class CancelSubscriptionService:
    def __init__(
        self,
        unit_of_work_factory: SubscriptionUnitOfWorkFactory,
        clock: Clock,
        lifecycle_service: SubscriptionLifecycleService,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock
        self._lifecycle_service = lifecycle_service

    async def execute(self, subscription_id: UUID) -> Subscription:
        async with self._unit_of_work_factory() as unit_of_work:
            subscription = await unit_of_work.subscriptions.get_by_id(subscription_id)
            if subscription is None:
                raise SubscriptionNotFoundError(str(subscription_id))
            updated = self._lifecycle_service.cancel(subscription, self._clock.now())
            await unit_of_work.subscriptions.save(updated)
            await unit_of_work.commit()
        return updated
