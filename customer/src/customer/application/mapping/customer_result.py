from customer.application.models.customer_result import CustomerResult
from customer.domain.customer import Customer


class CustomerResultMapper:
    def to_result(self, customer: Customer) -> CustomerResult:
        return CustomerResult(
            id=customer.id,
            business_id=customer.business_id,
            display_name=customer.display_name,
            status=customer.status,
            version=customer.version,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
        )
