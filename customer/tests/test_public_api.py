import subprocess
import sys

import customer


def test_core_import_has_no_optional_framework_dependencies() -> None:
    subprocess.run(
        [
            sys.executable,
            "-c",
            "import customer,sys; "
            "assert 'fastapi' not in sys.modules; assert 'sqlalchemy' not in sys.modules",
        ],
        check=True,
    )
    assert customer.CustomerModule


def test_public_exports_are_controlled() -> None:
    assert set(customer.__all__) == {
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
    }
