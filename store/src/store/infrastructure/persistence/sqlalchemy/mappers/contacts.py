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
        contacts: list[StoreContact] = []

        for record in records:
            label_value = record.get("label")
            label = label_value if isinstance(label_value, str) else None

            contacts.append(
                StoreContact(
                    type=StoreContactType(str(record["type"])),
                    value=str(record["value"]),
                    label=label,
                    is_primary=bool(record.get("is_primary", False)),
                )
            )

        return tuple(contacts)
