from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from customer.application.contracts.address_repository import CustomerAddressRepository
from customer.domain.address import CustomerAddress
from customer.infrastructure.persistence.sqlalchemy.mappers.address import AddressMapper
from customer.infrastructure.persistence.sqlalchemy.models import CustomerAddressModel


class SqlAlchemyAddressRepository(CustomerAddressRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_customer(
        self, business_id: UUID, customer_id: UUID
    ) -> tuple[CustomerAddress, ...]:
        rows = (
            await self.session.scalars(
                select(CustomerAddressModel)
                .where(
                    CustomerAddressModel.business_id == business_id,
                    CustomerAddressModel.customer_id == customer_id,
                )
                .order_by(CustomerAddressModel.id)
            )
        ).all()
        return tuple(AddressMapper.to_domain(row) for row in rows)

    async def get(
        self, business_id: UUID, customer_id: UUID, address_id: UUID
    ) -> CustomerAddress | None:
        row = await self.session.scalar(
            select(CustomerAddressModel).where(
                CustomerAddressModel.business_id == business_id,
                CustomerAddressModel.customer_id == customer_id,
                CustomerAddressModel.id == address_id,
            )
        )
        return AddressMapper.to_domain(row) if row is not None else None

    async def add(self, address: CustomerAddress) -> None:
        self.session.add(AddressMapper.to_row(address))

    async def save(self, address: CustomerAddress) -> None:
        await self.session.execute(
            update(CustomerAddressModel)
            .where(
                CustomerAddressModel.id == address.id,
                CustomerAddressModel.business_id == address.business_id,
                CustomerAddressModel.customer_id == address.customer_id,
            )
            .values(
                label=address.label,
                country_code=address.country_code,
                line1=address.line1,
                city=address.city,
                region=address.region,
                postal_code=address.postal_code,
                is_default=address.is_default,
            )
        )

    async def remove(self, business_id: UUID, customer_id: UUID, address_id: UUID) -> None:
        await self.session.execute(
            delete(CustomerAddressModel).where(
                CustomerAddressModel.business_id == business_id,
                CustomerAddressModel.customer_id == customer_id,
                CustomerAddressModel.id == address_id,
            )
        )

    async def unset_default(self, business_id: UUID, customer_id: UUID) -> None:
        await self.session.execute(
            update(CustomerAddressModel)
            .where(
                CustomerAddressModel.business_id == business_id,
                CustomerAddressModel.customer_id == customer_id,
            )
            .values(is_default=False)
        )
