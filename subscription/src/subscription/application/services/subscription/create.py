from subscription.application.contracts import SubscriptionUnitOfWorkFactory
from subscription.application.dto import CreateSubscriptionCommand
from subscription.application.errors import PlanNotFoundError, PlanUnavailableError
from subscription.application.mappers import CreateSubscriptionMapper
from subscription.domain import PlanStatus, Subscription


class CreateSubscriptionService:
    def __init__(
        self,
        unit_of_work_factory: SubscriptionUnitOfWorkFactory,
        mapper: CreateSubscriptionMapper,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._mapper = mapper

    async def execute(self, command: CreateSubscriptionCommand) -> Subscription:
        async with self._unit_of_work_factory() as unit_of_work:
            plan = await unit_of_work.plans.get_by_id(command.plan_id)
            if plan is None:
                raise PlanNotFoundError(str(command.plan_id))
            if plan.status is not PlanStatus.ACTIVE:
                raise PlanUnavailableError(plan.code.value)
            subscription = self._mapper.map(command, plan)
            await unit_of_work.subscriptions.add(subscription)
            await unit_of_work.commit()
        return subscription
