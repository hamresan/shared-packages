from decimal import Decimal

from store.domain import StoreCurrency


class StoreCurrencyPersistenceMapper:
    def to_records(self, currencies: tuple[StoreCurrency, ...]) -> list[dict[str, object]]:
        return [
            {"code": currency.code, "exchange_rate": str(currency.exchange_rate)}
            for currency in currencies
        ]

    def to_domain(self, records: list[dict[str, object]]) -> tuple[StoreCurrency, ...]:
        return tuple(
            StoreCurrency(
                code=str(record["code"]),
                exchange_rate=Decimal(str(record["exchange_rate"])),
            )
            for record in records
        )
