"""Public entry points for the reusable Customer package."""

from customer.application import (
    CustomerActor,
    CustomerActorType,
    CustomerAuthorizer,
    CustomerPermission,
    IdentityVerifier,
)
from customer.application.contracts.erasure_policy import CustomerErasurePolicy
from customer.application.contracts.external_identity_evidence import (
    ExternalIdentityEvidenceVerifier,
    VerifiedExternalIdentityEvidence,
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
from customer.application.models.external_identity_commands import (
    FindExternalIdentityQuery,
    GetOrCreateExternalIdentityCommand,
    LinkExternalIdentityCommand,
    RecordExternalIdentityVerificationCommand,
    RevokeExternalIdentityCommand,
)
from customer.application.models.identity_resolution import (
    CustomerResolution,
    InternalIdentityResolution,
)
from customer.application.models.internal_identity_commands import (
    LinkInternalIdentityCommand,
    ResolveInternalIdentityQuery,
)
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
    CustomerIdentityConflictError,
    CustomerIdentityVerificationError,
    CustomerInvalidStateError,
    CustomerNotFoundError,
    CustomerPermissionDeniedError,
    CustomerStatus,
    CustomerValidationError,
    CustomerVersionConflictError,
)
from customer.domain.contact import ContactKind
from customer.domain.external_identity import ExternalIdentityKey, ExternalIdentityStatus

__all__ = [
    "ExternalIdentityEvidenceVerifier",
    "VerifiedExternalIdentityEvidence",
    "CustomerIdentityConflictError",
    "CustomerIdentityVerificationError",
    "CustomerResolution",
    "ExternalIdentityKey",
    "ExternalIdentityStatus",
    "FindExternalIdentityQuery",
    "GetOrCreateExternalIdentityCommand",
    "InternalIdentityResolution",
    "LinkExternalIdentityCommand",
    "LinkInternalIdentityCommand",
    "RecordExternalIdentityVerificationCommand",
    "ResolveInternalIdentityQuery",
    "RevokeExternalIdentityCommand",
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
    "CustomerErasurePolicy",
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
