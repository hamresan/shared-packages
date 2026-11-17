"""Safe translation of expected customer errors into HTTP responses."""

from fastapi import HTTPException

from customer.domain.errors import (
    CustomerErasedError,
    CustomerIdempotencyConflictError,
    CustomerIdentityConflictError,
    CustomerIdentityVerificationError,
    CustomerInvalidStateError,
    CustomerNotFoundError,
    CustomerPermissionDeniedError,
    CustomerValidationError,
    CustomerVersionConflictError,
)


def customer_http_error(error: Exception) -> HTTPException:
    """Return stable, non-sensitive codes; never echo exception messages."""
    if isinstance(error, (CustomerNotFoundError, CustomerPermissionDeniedError)):
        return HTTPException(status_code=404, detail="customer_unavailable")
    if isinstance(error, CustomerVersionConflictError):
        return HTTPException(status_code=409, detail="version_conflict")
    if isinstance(error, CustomerIdempotencyConflictError):
        return HTTPException(status_code=409, detail="idempotency_conflict")
    if isinstance(error, CustomerIdentityConflictError):
        return HTTPException(status_code=409, detail="identity_conflict")
    if isinstance(error, CustomerIdentityVerificationError):
        return HTTPException(status_code=403, detail="identity_verification_required")
    if isinstance(error, (CustomerErasedError, CustomerInvalidStateError)):
        return HTTPException(status_code=409, detail="invalid_customer_state")
    if isinstance(error, CustomerValidationError):
        return HTTPException(status_code=422, detail="invalid_customer_input")
    raise error
