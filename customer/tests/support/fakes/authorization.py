from uuid import UUID

from customer import CustomerActor, CustomerAuthorizer, CustomerPermission


class AllowCustomerAuthorizer(CustomerAuthorizer):
    async def require_permission(
        self,
        actor: CustomerActor,
        permission: CustomerPermission,
        customer_id: UUID | None = None,
    ) -> None:
        return None
