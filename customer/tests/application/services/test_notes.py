from uuid import uuid4

import pytest

from customer import CustomerModule, CustomerModuleConfig, CustomerPermission
from customer.application.models import CreateCustomerCommand, GetCustomerQuery
from customer.application.models.note_commands import AddNoteCommand
from customer.application.models.profile_detail_commands import (
    CustomerChildMutation,
    CustomerDetailsQuery,
)
from customer.domain.errors import CustomerNotFoundError, CustomerPermissionDeniedError
from tests.support.factories.customer_module import build_actor, build_customer_module
from tests.support.fakes.authorization import DenyNotesAuthorizer


async def test_notes_are_separate_from_profile_and_have_author_provenance() -> None:
    module, _ = build_customer_module()
    actor = build_actor(uuid4())
    customer = await module.customers.create.execute(
        CreateCustomerCommand(actor.business_id, actor)
    )
    note = await module.notes.add.execute(
        AddNoteCommand(actor.business_id, actor, customer.id, "  Staff only  ")
    )
    assert (note.body, note.author_id, note.author_type) == ("Staff only", actor.actor_id, "user")
    profile = await module.customers.get.execute(
        GetCustomerQuery(actor.business_id, actor, customer.id)
    )
    assert not hasattr(profile, "notes")
    assert await module.notes.list.execute(
        CustomerDetailsQuery(actor.business_id, actor, customer.id)
    ) == (note,)
    await module.notes.remove.execute(
        CustomerChildMutation(actor.business_id, actor, customer.id, note.id)
    )
    assert not await module.notes.list.execute(
        CustomerDetailsQuery(actor.business_id, actor, customer.id)
    )
    with pytest.raises(CustomerNotFoundError):
        await module.notes.remove.execute(
            CustomerChildMutation(actor.business_id, actor, customer.id, note.id)
        )


async def test_note_access_uses_independent_permission() -> None:
    module, uow = build_customer_module()
    actor = build_actor(uuid4())
    customer = await module.customers.create.execute(
        CreateCustomerCommand(actor.business_id, actor)
    )
    limited = CustomerModule(
        CustomerModuleConfig(
            uow,
            DenyNotesAuthorizer(),
            module.config.identity_verifier,
            module.config.clock,
            module.config.identifiers,
            module.config.creation_fingerprinter,
            module.config.external_evidence_verifier,
        )
    )
    with pytest.raises(CustomerPermissionDeniedError):
        await limited.notes.list.execute(
            CustomerDetailsQuery(actor.business_id, actor, customer.id)
        )
    with pytest.raises(CustomerPermissionDeniedError):
        await limited.notes.add.execute(
            AddNoteCommand(actor.business_id, actor, customer.id, "Secret")
        )
    assert CustomerPermission.NOTES_READ.value == "customer.notes.read"
