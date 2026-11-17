"""Public grouping for narrowly scoped contact use cases."""

from dataclasses import dataclass

from customer.application.services.add_contact import AddContactService
from customer.application.services.list_contacts import ListContactsService
from customer.application.services.remove_contact import RemoveContactService
from customer.application.services.set_primary_contact import SetPrimaryContactService
from customer.application.services.update_contact import UpdateContactService


@dataclass(frozen=True, slots=True)
class ContactUseCases:
    add: AddContactService
    list: ListContactsService
    update: UpdateContactService
    set_primary: SetPrimaryContactService
    remove: RemoveContactService
