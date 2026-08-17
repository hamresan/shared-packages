from decimal import Decimal

from store.application.contracts import Clock, StoreIdentifierGenerator
from store.application.dto import CreateStoreCommand
from store.domain import Store, StoreCurrency


class StoreFactory:
    def __init__(self, identifier_generator: StoreIdentifierGenerator, clock: Clock) -> None:
        self._identifier_generator = identifier_generator
        self._clock = clock

    def create(self, command: CreateStoreCommand) -> Store:
        now = self._clock.now()
        return Store(
            id=self._identifier_generator.new_store_id(),
            owner_user_id=command.owner_user_id,
            name=command.name,
            business_type=command.business_type,
            primary_language=command.primary_language,
            supported_languages=(command.primary_language,),
            country_code=command.country_code,
            base_currency_code=command.base_currency_code,
            currencies=(
                StoreCurrency(code=command.base_currency_code, exchange_rate=Decimal("1")),
            ),
            created_at=now,
            updated_at=now,
        )
