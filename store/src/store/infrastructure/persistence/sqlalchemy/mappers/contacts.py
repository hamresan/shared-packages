from store.domain import StoreContact, StoreContactType


class StoreContactPersistenceMapper:
    def to_records(self, contacts: tuple[StoreContact, ...]) -> list[dict[str, object]]:
        return [
            {
                "type": contact.type.value,
                "value": contact.value,
                "label": contact.label,
                "is_primary": contact.is_primary,
            }
            for contact in contacts
        ]

    def to_domain(self, records: list[dict[str, object]]) -> tuple[StoreContact, ...]:
        return tuple(
            StoreContact(
                type=StoreContactType(str(record["type"])),
                value=str(record["value"]),
                label=record.get("label") if isinstance(record.get("label"), str) else None,
                is_primary=bool(record.get("is_primary", False)),
            )
            for record in records
        )
