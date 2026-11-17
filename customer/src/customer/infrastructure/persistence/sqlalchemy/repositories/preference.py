from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from customer.application.contracts.preference_repository import CustomerPreferenceRepository
from customer.domain.preference import CustomerPreference
from customer.infrastructure.persistence.sqlalchemy.mappers.preference import PreferenceMapper
from customer.infrastructure.persistence.sqlalchemy.models import CustomerPreferenceModel


class SqlAlchemyPreferenceRepository(CustomerPreferenceRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_customer(
        self, business_id: UUID, customer_id: UUID
    ) -> tuple[CustomerPreference, ...]:
        rows = (
            await self.session.scalars(
                select(CustomerPreferenceModel)
                .where(
                    CustomerPreferenceModel.business_id == business_id,
                    CustomerPreferenceModel.customer_id == customer_id,
                )
                .order_by(CustomerPreferenceModel.key)
            )
        ).all()
        return tuple(PreferenceMapper.to_domain(row) for row in rows)

    async def get(
        self, business_id: UUID, customer_id: UUID, key: str
    ) -> CustomerPreference | None:
        row = await self.session.scalar(
            select(CustomerPreferenceModel).where(
                CustomerPreferenceModel.business_id == business_id,
                CustomerPreferenceModel.customer_id == customer_id,
                CustomerPreferenceModel.key == key,
            )
        )
        return PreferenceMapper.to_domain(row) if row is not None else None

    async def upsert(self, preference: CustomerPreference) -> None:
        row = await self.session.scalar(
            select(CustomerPreferenceModel).where(
                CustomerPreferenceModel.business_id == preference.business_id,
                CustomerPreferenceModel.customer_id == preference.customer_id,
                CustomerPreferenceModel.key == preference.key,
            )
        )
        if row is None:
            self.session.add(PreferenceMapper.to_row(preference))
        else:
            row.value = preference.value

    async def remove(self, business_id: UUID, customer_id: UUID, key: str) -> None:
        await self.session.execute(
            delete(CustomerPreferenceModel).where(
                CustomerPreferenceModel.business_id == business_id,
                CustomerPreferenceModel.customer_id == customer_id,
                CustomerPreferenceModel.key == key,
            )
        )
