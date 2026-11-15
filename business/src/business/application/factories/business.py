from datetime import datetime

from business.application.contracts import IdentifierGenerator
from business.application.dto import CreateBusinessCommand
from business.domain.business import Business


class BusinessFactory:
    def __init__(self, identifier_generator: IdentifierGenerator) -> None:
        self._identifier_generator = identifier_generator

    def create(self, command: CreateBusinessCommand, *, created_at: datetime) -> Business:
        return Business(
            id=self._identifier_generator.new_id(),
            name=command.name,
            business_type=command.business_type,
            country_code=command.country_code,
            default_language=command.default_language,
            default_currency_code=command.default_currency_code,
            created_at=created_at,
            updated_at=created_at,
        )
