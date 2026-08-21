from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from subscription.application import PlanRepository
from subscription.domain import Plan, PlanCode
from subscription.infrastructure.persistence.sqlalchemy.mappers import PlanPersistenceMapper
from subscription.infrastructure.persistence.sqlalchemy.models import (
    PlanEntitlementModel,
    PlanModel,
)
from subscription.infrastructure.persistence.sqlalchemy.repositories.plan_hydrator import (
    SqlAlchemyPlanHydrator,
)


class SqlAlchemyPlanRepository(PlanRepository):
    def __init__(
        self,
        session: AsyncSession,
        mapper: PlanPersistenceMapper,
        hydrator: SqlAlchemyPlanHydrator,
    ) -> None:
        self._session = session
        self._mapper = mapper
        self._hydrator = hydrator

    async def get_by_id(self, plan_id: UUID) -> Plan | None:
        model = await self._session.get(PlanModel, str(plan_id))
        return None if model is None else await self._hydrator.hydrate(model)

    async def get_by_code(self, code: PlanCode) -> Plan | None:
        result = await self._session.execute(select(PlanModel).where(PlanModel.code == code.value))
        model = result.scalar_one_or_none()
        return None if model is None else await self._hydrator.hydrate(model)

    async def add(self, plan: Plan) -> None:
        self._session.add(self._mapper.to_model(plan))
        self._session.add_all(self._mapper.entitlement_models(plan))

    async def save(self, plan: Plan) -> None:
        await self._session.merge(self._mapper.to_model(plan))
        await self._session.execute(
            delete(PlanEntitlementModel).where(PlanEntitlementModel.plan_id == str(plan.id))
        )
        self._session.add_all(self._mapper.entitlement_models(plan))
