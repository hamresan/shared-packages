from uuid import UUID, uuid4

from customer.application.contracts import IdentifierGenerator


class RandomIdentifierGenerator(IdentifierGenerator):
    def new_id(self) -> UUID:
        return uuid4()
