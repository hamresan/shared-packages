from datetime import datetime

from business.application.contracts import IdentifierGenerator
from business.application.dto import CreateBranchCommand
from business.domain.branch import Branch


class BranchFactory:
    def __init__(self, identifier_generator: IdentifierGenerator) -> None:
        self._identifier_generator = identifier_generator

    def create(self, command: CreateBranchCommand, *, created_at: datetime) -> Branch:
        return Branch(
            id=self._identifier_generator.new_id(),
            business_id=command.business_id,
            name=command.name,
            timezone=command.timezone,
            address=command.address,
            contact=command.contact,
            created_at=created_at,
            updated_at=created_at,
        )
