from customer.domain.contact import ContactKind, CustomerContact
from customer.infrastructure.persistence.sqlalchemy.models import CustomerContactModel


class ContactMapper:
    @staticmethod
    def to_domain(row: CustomerContactModel) -> CustomerContact:
        return CustomerContact(
            id=row.id,
            business_id=row.business_id,
            customer_id=row.customer_id,
            kind=ContactKind(row.kind),
            value=row.value,
            is_primary=row.is_primary,
            created_at=row.created_at,
            verified_at=row.verified_at,
            verification_method=row.verification_method,
        )

    @staticmethod
    def to_row(value: CustomerContact) -> CustomerContactModel:
        return CustomerContactModel(
            id=value.id,
            business_id=value.business_id,
            customer_id=value.customer_id,
            kind=value.kind.value,
            value=value.value,
            is_primary=value.is_primary,
            created_at=value.created_at,
            verified_at=value.verified_at,
            verification_method=value.verification_method,
        )
