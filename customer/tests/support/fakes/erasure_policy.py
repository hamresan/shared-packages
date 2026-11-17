from uuid import UUID

from customer.application.actor import CustomerActor
from customer.application.contracts.erasure_policy import CustomerErasurePolicy
from customer.domain.errors import CustomerPermissionDeniedError


class AllowErasurePolicy(CustomerErasurePolicy):
    async def require_allowed(
        self, actor: CustomerActor, business_id: UUID, customer_id: UUID
    ) -> None:
        return None


class DenyErasurePolicy(CustomerErasurePolicy):
    async def require_allowed(
        self, actor: CustomerActor, business_id: UUID, customer_id: UUID
    ) -> None:
        raise CustomerPermissionDeniedError("Retention hold")
