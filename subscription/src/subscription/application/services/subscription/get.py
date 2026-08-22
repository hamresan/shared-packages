from uuid import UUID

from subscription.application.contracts import SubscriptionUnitOfWorkFactory
from subscription.application.errors import SubscriptionNotFoundError
from subscription.domain import Subscription


class GetSubscriptionService:
    def __init__(self, unit_of_work_factory: SubscriptionUnitOfWorkFactory) -> None:
        self._unit_of_work_factory = unit_of_work_factory

    async def execute(self, subscription_id: UUID) -> Subscription:
        async with self._unit_of_work_factory() as unit_of_work:
            subscription = await unit_of_work.subscriptions.get_by_id(subscription_id)
        if subscription is None:
            raise SubscriptionNotFoundError(str(subscription_id))
        return subscription
