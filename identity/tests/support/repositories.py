from uuid import UUID

from identity.application.contracts.repositories import UserIdentityRepository, UserRepository
from identity.domain import IdentityType, User, UserIdentity


class FakeUserRepository(UserRepository):
    def __init__(self, users: list[User] | None = None) -> None:
        self.users = {user.id: user for user in users or []}
        self.added: list[User] = []

    async def get(self, user_id: UUID) -> User | None:
        return self.users.get(user_id)

    async def add(self, user: User) -> None:
        self.users[user.id] = user
        self.added.append(user)


class FakeUserIdentityRepository(UserIdentityRepository):
    def __init__(self) -> None:
        self.identities: list[UserIdentity] = []

    async def get_by_destination(
        self,
        identity_type: IdentityType,
        normalized_value: str,
    ) -> UserIdentity | None:
        return next(
            (
                identity
                for identity in self.identities
                if identity.type is identity_type
                and identity.normalized_value == normalized_value
            ),
            None,
        )

    async def add(self, identity: UserIdentity) -> None:
        self.identities.append(identity)
