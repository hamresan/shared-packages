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

__all__ = [
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
