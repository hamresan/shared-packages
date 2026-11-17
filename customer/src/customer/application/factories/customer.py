from datetime import datetime
from uuid import UUID

from customer.domain.customer import Customer, CustomerStatus


class CustomerFactory:
    def create(
        self, customer_id: UUID, business_id: UUID, display_name: str | None, now: datetime
    ) -> Customer:
        return Customer(
            id=customer_id,
            business_id=business_id,
            display_name=display_name,
            status=CustomerStatus.ACTIVE,
            version=1,
            created_at=now,
            updated_at=now,
        )
