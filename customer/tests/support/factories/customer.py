"""PostgreSQL acceptance fixture data for an independent Customer aggregate."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from customer.domain.customer import Customer, CustomerStatus


def new_customer(business_id: UUID, customer_id: UUID | None = None) -> Customer:
    now = datetime.now(UTC)
    return Customer(
        id=customer_id or uuid4(),
        business_id=business_id,
        display_name="Example",
        status=CustomerStatus.ACTIVE,
        version=1,
        created_at=now,
        updated_at=now,
    )
