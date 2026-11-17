import sys

import customer


def test_core_import_has_no_optional_framework_dependencies() -> None:
    assert "fastapi" not in sys.modules
    assert "sqlalchemy" not in sys.modules
    assert customer.CustomerModule


def test_public_exports_are_controlled() -> None:
    assert set(customer.__all__) == {
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
    }
