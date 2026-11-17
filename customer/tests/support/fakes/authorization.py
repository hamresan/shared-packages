from uuid import UUID

from customer import CustomerActor, CustomerAuthorizer, CustomerPermission
from customer.domain import CustomerPermissionDeniedError


class AllowCustomerAuthorizer(CustomerAuthorizer):
    async def require_permission(
        self,
        actor: CustomerActor,
        permission: CustomerPermission,
        customer_id: UUID | None = None,
    ) -> None:
        return None


class DenyCustomerAuthorizer(CustomerAuthorizer):
    async def require_permission(
        self,
        actor: CustomerActor,
        permission: CustomerPermission,
        customer_id: UUID | None = None,
    ) -> None:
        raise CustomerPermissionDeniedError("Denied by host authorization")
