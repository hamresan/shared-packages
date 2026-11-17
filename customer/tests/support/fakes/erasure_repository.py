from uuid import UUID

from customer.application.contracts.erasure_repository import CustomerErasureRepository
from tests.support.fakes.address_repository import InMemoryAddressRepository
from tests.support.fakes.contact_repository import InMemoryContactRepository
from tests.support.fakes.external_identity_repository import InMemoryExternalIdentityRepository
from tests.support.fakes.idempotency_repository import InMemoryCustomerIdempotencyRepository
from tests.support.fakes.internal_identity_repository import InMemoryIdentityLinkRepository
from tests.support.fakes.note_repository import InMemoryNoteRepository
from tests.support.fakes.preference_repository import InMemoryPreferenceRepository


class InMemoryErasureRepository(CustomerErasureRepository):
    def __init__(
        self,
        contacts: InMemoryContactRepository,
        addresses: InMemoryAddressRepository,
        preferences: InMemoryPreferenceRepository,
        notes: InMemoryNoteRepository,
        internal: InMemoryIdentityLinkRepository,
        external: InMemoryExternalIdentityRepository,
        idempotency: InMemoryCustomerIdempotencyRepository,
    ) -> None:
        self.contacts = contacts
        self.addresses = addresses
        self.preferences = preferences
        self.notes = notes
        self.internal = internal
        self.external = external
        self.idempotency = idempotency

    async def erase_children(self, business_id: UUID, customer_id: UUID) -> None:
        for key in list(self.contacts.records):
            if key[:2] == (business_id, customer_id):
                del self.contacts.records[key]
        for key in list(self.addresses.records):
            if key[:2] == (business_id, customer_id):
                del self.addresses.records[key]
        for key in list(self.preferences.records):
            if key[:2] == (business_id, customer_id):
                del self.preferences.records[key]
        for key in list(self.notes.records):
            if key[:2] == (business_id, customer_id):
                del self.notes.records[key]
        self.internal.links = [
            item
            for item in self.internal.links
            if item.business_id != business_id or item.customer_id != customer_id
        ]
        self.external.identities = [
            item
            for item in self.external.identities
            if item.key.business_id != business_id or item.customer_id != customer_id
        ]
        self.idempotency.records = {
            key: value
            for key, value in self.idempotency.records.items()
            if value.business_id != business_id or value.customer_id != customer_id
        }
