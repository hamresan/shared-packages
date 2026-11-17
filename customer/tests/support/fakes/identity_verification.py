from uuid import UUID

from customer import IdentityVerifier


class AcceptIdentityVerifier(IdentityVerifier):
    async def require_valid_user(self, identity_user_id: UUID) -> None:
        return None
