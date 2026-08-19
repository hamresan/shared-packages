from typing import Protocol
from uuid import UUID

from identity.domain import User


class UserReader(Protocol):
    async def get_by_id(self, user_id: UUID) -> User | None: ...
