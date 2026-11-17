from customer.domain.customer import Customer, CustomerStatus
from customer.infrastructure.persistence.sqlalchemy.models import CustomerModel


class CustomerMapper:
    @staticmethod
    def to_domain(row: CustomerModel) -> Customer:
        return Customer(
            id=row.id,
            business_id=row.business_id,
            display_name=row.display_name,
            status=CustomerStatus(row.status),
            version=row.version,
            created_at=row.created_at,
            updated_at=row.updated_at,
            archived_at=row.archived_at,
            erased_at=row.erased_at,
        )

    @staticmethod
    def to_row(value: Customer) -> CustomerModel:
        return CustomerModel(
            id=value.id,
            business_id=value.business_id,
            display_name=value.display_name,
            status=value.status.value,
            version=value.version,
            created_at=value.created_at,
            updated_at=value.updated_at,
            archived_at=value.archived_at,
            erased_at=value.erased_at,
        )
