from uuid import UUID

from customer import CustomerActor, IdentityVerifier
from customer.domain.errors import CustomerIdentityVerificationError


class AcceptIdentityVerifier(IdentityVerifier):
    async def require_linkable_user(
        self, identity_user_id: UUID, actor: CustomerActor, customer_id: UUID
    ) -> None:
        return None


class RejectIdentityVerifier(IdentityVerifier):
    async def require_linkable_user(
        self, identity_user_id: UUID, actor: CustomerActor, customer_id: UUID
    ) -> None:
        raise CustomerIdentityVerificationError("Internal identity user is not valid")
