"""Host-injected example: contacts and structured preferences."""

from uuid import UUID

from customer import (
    AddContactCommand,
    ContactKind,
    ContactResult,
    CustomerActor,
    CustomerModule,
    PreferenceResult,
    SetPreferenceCommand,
)


async def save_contact_and_language(
    module: CustomerModule, actor: CustomerActor, customer_id: UUID
) -> tuple[ContactResult, PreferenceResult]:
    contact = await module.contacts.add.execute(
        AddContactCommand(
            business_id=actor.business_id,
            actor=actor,
            customer_id=customer_id,
            kind=ContactKind.EMAIL,
            value="alex@example.com",
            is_primary=True,
        )
    )
    preference = await module.preferences.set.execute(
        SetPreferenceCommand(actor.business_id, actor, customer_id, "language", "en")
    )
    return contact, preference
