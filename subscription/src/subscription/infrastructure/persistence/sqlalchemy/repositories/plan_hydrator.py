from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from subscription.domain import Plan
from subscription.infrastructure.persistence.sqlalchemy.mappers import PlanPersistenceMapper
from subscription.infrastructure.persistence.sqlalchemy.models import (
    PlanEntitlementModel,
    PlanModel,
)


class SqlAlchemyPlanHydrator:
    def __init__(self, session: AsyncSession, mapper: PlanPersistenceMapper) -> None:
        self._session = session
        self._mapper = mapper

    async def hydrate(self, model: PlanModel) -> Plan:
        result = await self._session.execute(
            select(PlanEntitlementModel).where(PlanEntitlementModel.plan_id == model.id)
        )
        return self._mapper.to_domain(model, tuple(result.scalars().all()))
