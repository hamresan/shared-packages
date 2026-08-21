from dataclasses import replace
from uuid import UUID

from subscription.application.contracts import SubscriptionUnitOfWorkFactory
from subscription.application.errors import PlanNotFoundError
from subscription.domain import Plan, PlanStatus, PlanStatusTransitionPolicy


class ChangePlanStatusService:
    def __init__(
        self,
        unit_of_work_factory: SubscriptionUnitOfWorkFactory,
        transition_policy: PlanStatusTransitionPolicy,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._transition_policy = transition_policy

    async def execute(self, plan_id: UUID, target: PlanStatus) -> Plan:
        async with self._unit_of_work_factory() as unit_of_work:
            plan = await unit_of_work.plans.get_by_id(plan_id)
            if plan is None:
                raise PlanNotFoundError(str(plan_id))
            self._transition_policy.validate(plan.status, target)
            updated = replace(plan, status=target)
            await unit_of_work.plans.save(updated)
            await unit_of_work.commit()
        return updated
