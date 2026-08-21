from subscription.application.contracts import SubscriptionUnitOfWorkFactory
from subscription.application.dto import CreatePlanCommand
from subscription.application.errors import PlanCodeAlreadyExistsError
from subscription.application.mappers import CreatePlanMapper
from subscription.domain import Plan


class CreatePlanService:
    def __init__(
        self,
        unit_of_work_factory: SubscriptionUnitOfWorkFactory,
        mapper: CreatePlanMapper,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._mapper = mapper

    async def execute(self, command: CreatePlanCommand) -> Plan:
        plan = self._mapper.map(command)
        async with self._unit_of_work_factory() as unit_of_work:
            existing = await unit_of_work.plans.get_by_code(plan.code)
            if existing is not None:
                raise PlanCodeAlreadyExistsError(plan.code.value)
            await unit_of_work.plans.add(plan)
            await unit_of_work.commit()
        return plan
