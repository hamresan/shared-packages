from uuid import UUID, uuid4

from business.application.contracts import IdentifierGenerator


class UuidIdentifierGenerator(IdentifierGenerator):
    def new_id(self) -> UUID:
        return uuid4()
