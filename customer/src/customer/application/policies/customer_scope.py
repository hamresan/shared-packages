from uuid import UUID

from customer.application.actor import CustomerActor
from customer.domain.errors import CustomerPermissionDeniedError


class CustomerScopePolicy:
    def require_matching_business(self, business_id: UUID, actor: CustomerActor) -> None:
        if actor.business_id != business_id:
            raise CustomerPermissionDeniedError("Customer operation is not permitted")
