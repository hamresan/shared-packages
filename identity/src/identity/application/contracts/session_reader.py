from typing import Protocol
from uuid import UUID

from identity.domain import Session


class SessionReader(Protocol):
    async def get_by_id(self, session_id: UUID) -> Session | None: ...
