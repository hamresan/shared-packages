from typing import Protocol
from uuid import UUID


class IdentifierGenerator(Protocol):
    def new_id(self) -> UUID: ...
