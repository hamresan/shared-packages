"""Framework-independent Customer domain."""

from customer.domain.customer import Customer, CustomerStatus
from customer.domain.errors import (
    CustomerErasedError,
    CustomerError,
    CustomerIdempotencyConflictError,
    CustomerInvalidStateError,
    CustomerNotFoundError,
    CustomerPermissionDeniedError,
    CustomerValidationError,
    CustomerVersionConflictError,
)

__all__ = [
    "Customer",
    "CustomerErasedError",
    "CustomerError",
    "CustomerIdempotencyConflictError",
    "CustomerInvalidStateError",
    "CustomerNotFoundError",
    "CustomerPermissionDeniedError",
    "CustomerStatus",
    "CustomerValidationError",
    "CustomerVersionConflictError",
]
