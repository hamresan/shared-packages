from uuid import UUID

from business.application.contracts import IdentifierGenerator


class SequentialIdentifierGenerator(IdentifierGenerator):
    def __init__(self, identifiers: tuple[UUID, ...]) -> None:
        self._identifiers = iter(identifiers)

    def new_id(self) -> UUID:
        return next(self._identifiers)
