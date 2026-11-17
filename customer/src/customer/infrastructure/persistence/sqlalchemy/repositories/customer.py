from uuid import UUID

from sqlalchemy import CursorResult, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from customer.application.contracts.customer_repository import CustomerRepository
from customer.domain.customer import Customer
from customer.domain.errors import CustomerVersionConflictError
from customer.infrastructure.persistence.sqlalchemy.mappers.customer import CustomerMapper
from customer.infrastructure.persistence.sqlalchemy.models import CustomerModel


class SqlAlchemyCustomerRepository(CustomerRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, business_id: UUID, customer_id: UUID) -> Customer | None:
        row = await self.session.scalar(
            select(CustomerModel).where(
                CustomerModel.business_id == business_id, CustomerModel.id == customer_id
            )
        )
        return CustomerMapper.to_domain(row) if row is not None else None

    async def add(self, customer: Customer) -> None:
        self.session.add(CustomerMapper.to_row(customer))

    async def save(self, customer: Customer, expected_version: int) -> None:
        result = await self.session.execute(
            update(CustomerModel)
            .where(
                CustomerModel.id == customer.id,
                CustomerModel.business_id == customer.business_id,
                CustomerModel.version == expected_version,
            )
            .values(
                display_name=customer.display_name,
                status=customer.status.value,
                version=customer.version,
                updated_at=customer.updated_at,
                archived_at=customer.archived_at,
                erased_at=customer.erased_at,
            )
        )
        if not isinstance(result, CursorResult) or result.rowcount != 1:
            raise CustomerVersionConflictError("Customer was changed by another operation")

    async def search(
        self, business_id: UUID, name_contains: str | None, offset: int, limit: int
    ) -> tuple[Customer, ...]:
        statement = select(CustomerModel).where(CustomerModel.business_id == business_id)
        if name_contains is not None:
            statement = statement.where(
                CustomerModel.display_name.ilike(
                    f"%{name_contains.replace('%', r'\%').replace('_', r'\_')}%", escape="\\"
                )
            )
        rows = (
            await self.session.scalars(
                statement.order_by(CustomerModel.created_at, CustomerModel.id)
                .offset(offset)
                .limit(limit)
            )
        ).all()
        return tuple(CustomerMapper.to_domain(row) for row in rows)
