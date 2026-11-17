"""Remove all Customer-owned PII without touching external historical records."""

from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from customer.application.contracts.erasure_repository import CustomerErasureRepository
from customer.infrastructure.persistence.sqlalchemy.models import (
    CustomerAddressModel,
    CustomerContactModel,
    CustomerCreationReceiptModel,
    CustomerExternalIdentityModel,
    CustomerIdentityLinkModel,
    CustomerNoteModel,
    CustomerPreferenceModel,
)


class SqlAlchemyErasureRepository(CustomerErasureRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def erase_children(self, business_id: UUID, customer_id: UUID) -> None:
        for model in (
            CustomerContactModel,
            CustomerAddressModel,
            CustomerPreferenceModel,
            CustomerNoteModel,
            CustomerIdentityLinkModel,
            CustomerExternalIdentityModel,
            CustomerCreationReceiptModel,
        ):
            await self.session.execute(
                delete(model).where(
                    model.business_id == business_id,
                    model.customer_id == customer_id,
                )
            )
