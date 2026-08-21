from uuid import UUID

from subscription.application.contracts import SubscriptionUnitOfWorkFactory
from subscription.application.errors import PlanNotFoundError
from subscription.domain import Plan


class GetPlanService:
    def __init__(self, unit_of_work_factory: SubscriptionUnitOfWorkFactory) -> None:
        self._unit_of_work_factory = unit_of_work_factory

    async def execute(self, plan_id: UUID) -> Plan:
        async with self._unit_of_work_factory() as unit_of_work:
            plan = await unit_of_work.plans.get_by_id(plan_id)
        if plan is None:
            raise PlanNotFoundError(str(plan_id))
        return plan
