from subscription.application.contracts import Clock, SubscriptionUnitOfWorkFactory
from subscription.application.dto import GetUsageCounterQuery
from subscription.domain import UsageCounter


class GetUsageCounterService:
    def __init__(
        self,
        unit_of_work_factory: SubscriptionUnitOfWorkFactory,
        clock: Clock,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock

    async def execute(self, query: GetUsageCounterQuery) -> UsageCounter:
        async with self._unit_of_work_factory() as unit_of_work:
            return await unit_of_work.usage.get_counter(
                query.subject,
                query.metric,
                query.period,
                self._clock.now(),
            )
