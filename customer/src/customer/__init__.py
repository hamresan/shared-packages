"""Public entry points for the reusable Customer package."""

from customer.application import (
    CustomerActor,
    CustomerActorType,
    CustomerAuthorizer,
    CustomerPermission,
    IdentityVerifier,
)
from customer.application.models import (
    CreateCustomerCommand,
    CustomerMutationCommand,
    CustomerResult,
    CustomerSearchQuery,
    CustomerSearchResult,
    GetCustomerQuery,
    UpdateCustomerCommand,
)
from customer.application.models.address_commands import AddAddressCommand, UpdateAddressCommand
from customer.application.models.address_result import AddressResult
from customer.application.models.contact_commands import (
    AddContactCommand,
    ContactMutationCommand,
    ListContactsQuery,
    UpdateContactCommand,
)
from customer.application.models.contact_result import ContactResult
from customer.application.models.note_commands import AddNoteCommand
from customer.application.models.note_result import NoteResult
from customer.application.models.preference_commands import (
    RemovePreferenceCommand,
    SetPreferenceCommand,
)
from customer.application.models.preference_result import PreferenceResult
from customer.application.models.profile_detail_commands import (
    CustomerChildMutation,
    CustomerDetailsQuery,
)
from customer.bootstrap import CustomerModule, CustomerModuleConfig
from customer.domain import (
    CustomerErasedError,
    CustomerError,
    CustomerIdempotencyConflictError,
    CustomerInvalidStateError,
    CustomerNotFoundError,
    CustomerPermissionDeniedError,
    CustomerStatus,
    CustomerValidationError,
    CustomerVersionConflictError,
)
from customer.domain.contact import ContactKind

__all__ = [
    "AddAddressCommand",
    "AddContactCommand",
    "AddNoteCommand",
    "AddressResult",
    "ContactKind",
    "ContactMutationCommand",
    "ContactResult",
    "CustomerChildMutation",
    "CustomerDetailsQuery",
    "ListContactsQuery",
    "NoteResult",
    "PreferenceResult",
    "RemovePreferenceCommand",
    "SetPreferenceCommand",
    "UpdateAddressCommand",
    "UpdateContactCommand",
    "CustomerActor",
    "CustomerActorType",
    "CustomerAuthorizer",
    "CreateCustomerCommand",
    "CustomerErasedError",
    "CustomerError",
    "CustomerIdempotencyConflictError",
    "CustomerInvalidStateError",
    "CustomerModule",
    "CustomerModuleConfig",
    "CustomerMutationCommand",
    "CustomerNotFoundError",
    "CustomerPermission",
    "CustomerPermissionDeniedError",
    "CustomerResult",
    "CustomerSearchQuery",
    "CustomerSearchResult",
    "CustomerStatus",
    "CustomerValidationError",
    "CustomerVersionConflictError",
    "GetCustomerQuery",
    "IdentityVerifier",
    "UpdateCustomerCommand",
]
