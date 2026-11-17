from fastapi import HTTPException

from customer.domain.errors import (
    CustomerIdempotencyConflictError,
    CustomerNotFoundError,
    CustomerPermissionDeniedError,
    CustomerValidationError,
    CustomerVersionConflictError,
)
from customer.presentation.http.error_mapping import customer_http_error


def test_unknown_or_forbidden_customer_is_indistinguishable() -> None:
    for error in (CustomerNotFoundError("secret"), CustomerPermissionDeniedError("secret")):
        response = customer_http_error(error)
        assert response.status_code == 404
        assert response.detail == "customer_unavailable"
        assert "secret" not in str(response.detail)


def test_safe_conflict_and_validation_codes() -> None:
    examples = (
        (CustomerVersionConflictError("hidden"), 409, "version_conflict"),
        (CustomerIdempotencyConflictError("hidden"), 409, "idempotency_conflict"),
        (CustomerValidationError("hidden"), 422, "invalid_customer_input"),
    )
    for error, status, code in examples:
        response: HTTPException = customer_http_error(error)
        assert (response.status_code, response.detail) == (status, code)
