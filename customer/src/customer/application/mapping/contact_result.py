from customer.application.models.contact_result import ContactResult
from customer.domain.contact import CustomerContact


class ContactResultMapper:
    def to_result(self, contact: CustomerContact) -> ContactResult:
        return ContactResult(
            contact.id,
            contact.business_id,
            contact.customer_id,
            contact.kind,
            contact.value,
            contact.is_primary,
            contact.verified_at is not None,
        )
